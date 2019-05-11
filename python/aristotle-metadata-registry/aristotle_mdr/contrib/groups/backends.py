from typing import Optional, List
from braces.views import (
    LoginRequiredMixin, PermissionRequiredMixin, SuperuserRequiredMixin
)

import os

from django.conf.urls import url, include
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    RedirectView,
)
from django.template import loader
from django.contrib import messages

from organizations.backends.defaults import InvitationBackend

import attr

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.http import Http404

from .base import AbstractGroup
from .utils import GroupRegistrationTokenGenerator

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

User = get_user_model()


class ListForObjectMixin(DetailView):
    related_class = None

    def get_object(self):
        self.object = DetailView.get_object(self, queryset=self.related_class.objects.all())
        return self.object


class GroupTemplateMixin(object):
    fallback_template_name: Optional[str] = None

    def get_template_names(self):
        try:
            templates = super().get_template_names()
            if self.manager.template_base_directory:
                templates = [
                    os.path.join(self.manager.template_base_directory, t)
                    for t in templates
                ]
        except:
            templates = []
        if self.fallback_template_name:
            templates += [self.fallback_template_name]
        return templates


class GroupBase(GroupTemplateMixin):
    manager = None
    slug_url_kwarg = "group_slug"
    group_class = AbstractGroup
    group_slug_url_kwarg = "group_slug"
    superuser_override = True
    group_context_name = None

    def get_group_queryset(self):
        if getattr(self, 'model', None) and issubclass(self.model, self.group_class):
            qs = super().get_queryset()
        else:
            qs = self.group_class.objects.all()
        qs = qs.prefetch_related('members')
        if self.request.user.is_anonymous():
            return qs
        return qs


class GroupMixin(GroupBase):
    current_group_context = ""

    def get_group_context_name(self):
        for obj in [self, self.manager]:
            name = getattr(obj, "group_context_name", None)
            if name is not None:
                return name
        return "group"

    def get_group(self):
        if getattr(self, 'model', None) is not None and issubclass(self.model, self.group_class):
            slug = self.slug_url_kwarg
        else:
            slug = self.group_slug_url_kwarg
        return get_object_or_404(
            self.get_group_queryset(), slug=self.kwargs[slug]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({self.get_group_context_name(): self.get_group()})
        context.update({"group": self.get_group()})
        context.update({"active_group_page": self.current_group_context})
        return context


class GroupMemberMixin(GroupMixin):
    def get_member(self):
        return get_object_or_404(
            self.get_group().member_list, pk=self.kwargs['member_pk']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['member'] = self.get_member()
        context['current_roles'] = self.get_group().roles_for_user(self.get_member())
        return context


class IsGroupMemberMixin(PermissionRequiredMixin):
    def check_permissions(self, request):
        return self.get_group().has_member(request.user)


class HasRoleMixin(PermissionRequiredMixin):
    role = None

    def check_permissions(self, request):
        assert self.role is not None
        self.group = self.get_group()
        return self.group.has_role(request.user, self.role)


class HasRolePermissionMixin(PermissionRequiredMixin):
    role_permission: Optional[str] = None
    raise_exception = True
    redirect_unauthenticated_users = True

    def check_permissions(self, request):
        assert self.role_permission is not None
        self.group = self.get_group()
        can_access = self.group.user_has_permission(user=request.user, permission=self.role_permission)
        return can_access


class GroupListView(LoginRequiredMixin, GroupBase, ListView):
    fallback_template_name = "groups/group/list.html"
    superuser_override = False

    def get_queryset(self):
        return super().get_group_queryset().group_list_for_user(self.request.user)


class GroupListAllView(SuperuserRequiredMixin, GroupListView):
    fallback_template_name = "groups/group/list.html"
    superuser_override = True


class GroupMemberListView(LoginRequiredMixin, HasRolePermissionMixin, GroupMixin, ListView):
    fallback_template_name = "groups/group/members/list.html"
    role_permission = "edit_members"
    current_group_context = "members"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(group=self.get_group())


class GroupMemberRemoveView(LoginRequiredMixin, HasRolePermissionMixin, GroupMemberMixin, FormView):
    fallback_template_name = "groups/group/members/remove.html"
    role_permission = "edit_members"
    form_class = forms.Form  # We literally just need a blank form

    def form_valid(self, form):
        self.get_group().members.filter(user=self.kwargs['member_pk']).delete()

        return HttpResponseRedirect(
            reverse("%s:%s" % (self.manager.namespace, "detail"), args=[self.group.slug])
        )


class GroupDetailView(HasRolePermissionMixin, GroupMixin, DetailView):
    fallback_template_name = "groups/group/detail.html"
    role_permission = "view_group"
    current_group_context = "home"


class GroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, GroupBase, CreateView):
    fallback_template_name = "groups/group/create.html"
    role_permission = "edit_group_details"
    manager = None
    fields = ['name', 'description']

    def get_permission_required(self, request=None):
        perm = "{}.add_{}".format(
            self.manager.group_class._meta.app_label,
            self.manager.group_class._meta.model_name,
        )
        return perm

    def get_success_url(self):
        return reverse("%s:%s" % (self.manager.namespace, "detail"), args=[self.object.slug])


class GroupUpdateView(LoginRequiredMixin, HasRolePermissionMixin, GroupMixin, UpdateView):
    fallback_template_name = "groups/group/update.html"
    role_permission = "edit_group_details"
    current_group_context = "settings"

    def get_success_url(self):
        return reverse("%s:%s" % (self.manager.namespace, "detail"), args=[self.object.slug])


class MembershipUpdateForm(forms.Form):
    def __init__(self, manager, group, member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.group = group
        self.member = member
        if self.manager.group_class.allows_multiple_roles:
            self.fields['role'] = forms.MultipleChoiceField(
                choices=self.group.roles,
                widget=forms.CheckboxSelectMultiple,
                label=_("Roles"),
                required=False,
                initial=self.group.roles_for_user(member),
            )
        else:
            self.fields['role'] = forms.ChoiceField(
                choices=self.group.roles,
                label=_("Role"),
                required=True,
                initial=self.group.roles_for_user(member),
            )


class GroupMembershipFormView(LoginRequiredMixin, HasRolePermissionMixin, GroupMemberMixin, DetailView, FormView):
    template_name = "groups/group/members/update.html"
    role_permission = "edit_members"
    membership_class = None
    form_class = MembershipUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['group'] = self.get_group()
        kwargs['manager'] = self.manager
        kwargs['member'] = self.get_member()
        return kwargs

    def get_success_url(self):
        return reverse("%s:%s" % (self.manager.namespace, "member_list"), args=[self.group.slug])

    def form_valid(self, form):
        self.get_group().grant_role(form.cleaned_data['role'], user=self.get_member())
        return super().form_valid(form)


class GroupMemberAddView(LoginRequiredMixin, HasRolePermissionMixin, GroupMixin, CreateView):
    fallback_template_name = "groups/group/members/add.html"
    role_permission = "edit_members"

    def get_form_class(self):
        class MembershipCreateForm(forms.ModelForm):
            class Meta:
                fields = ["user", "role"]
                model = self.manager.membership_class

            def __init__(self, manager, group, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.manager = manager
                self.group = group

                self.fields['user'].queryset = get_user_model().objects.all().exclude(
                    pk__in=self.group.member_list.all())

        return MembershipCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['group'] = self.get_group()
        kwargs['manager'] = self.manager
        return kwargs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['active_group_page'] = 'members'

        return context

    def form_valid(self, form):
        form.instance.group = self.get_group()
        messages.success(self.request, 'User added successfully.')
        return super().form_valid(form)

    def get_initial(self):
        initial = self.initial.copy()
        initial.update({"group": self.get_group()})
        return initial

    def get_success_url(self):
        return reverse("%s:%s" % (self.manager.namespace, "detail"), args=[self.group.slug])


@attr.s
class GroupURLManager(InvitationBackend):
    """
    A backend for allowing new users to join the site by creating a new user
    associated with a new organization.
    """
    group_class = attr.ib()
    membership_class = attr.ib()
    namespace = attr.ib()
    update_fields: List = attr.ib(default=[])
    url_path = ""
    template_base_directory = None

    # form_class = forms.AristotleUserRegistrationForm

    def group_meta(self):
        return self.group_class._meta

    def get_success_url(self):
        return reverse('friendly_login') + '?welcome=true'

    def get_extra_group_urls(self):
        return []

    def get_urls(self):

        return [
            url(r'^s/?$', view=self.list_view(), name="list"),
            url(r'^/?$', view=RedirectView.as_view(pattern_name=self.namespace + ":list")),
            url(r'^s/create/$', view=self.create_view(), name="create"),
            url(r'^s/all/$', view=self.list_all_view(), name="list_all"),

            url("^/(?P<group_slug>[-\w]+)/", include([
                url("^$", view=self.detail_view(), name="detail"),
                url("settings", view=self.update_view(), name="settings"),
                url("", include(self.get_extra_group_urls()))
            ])),
            url("^/(?P<group_slug>[-\w]+)/members/", include([
                url(r'^$', view=self.membership_list_view(), name="member_list"),
                url(r'^add$', view=self.membership_add_view(), name="member_add"),
                url(r'^(?P<member_pk>[\d]+)/?$', view=self.membership_update_view(), name="membership_update"),
                url(r'^(?P<member_pk>[\d]+)/remove', view=self.membership_remove_view(), name="membership_remove"),
                url(r'^invite$', view=self.invite_view(), name="invite"),
                url(
                    r'^accept-invitation/(?P<user_id>[\d]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                    view=self.activate_view(),
                    name="accept_invitation"
                ),
            ]))
        ]

    def create_view(self, *args, **kwargs):
        return GroupCreateView.as_view(manager=self, model=self.group_class, *args, **kwargs)

    def list_all_view(self, *args, **kwargs):
        return GroupListAllView.as_view(manager=self, model=self.group_class, *args, **kwargs)

    def list_view(self, *args, **kwargs):
        return GroupListView.as_view(manager=self, model=self.group_class, *args, **kwargs)

    def detail_view(self, *args, **kwargs):
        return GroupDetailView.as_view(manager=self, model=self.group_class, *args, **kwargs)

    def membership_add_view(self, *args, **kwargs):
        return GroupMemberAddView.as_view(
            manager=self,
            group_class=self.group_class,
            model=self.membership_class,
            *args, **kwargs
        )

    def membership_remove_view(self, *args, **kwargs):
        return GroupMemberRemoveView.as_view(
            manager=self,
            group_class=self.group_class,
            *args, **kwargs
        )

    def membership_list_view(self, *args, **kwargs):
        return GroupMemberListView.as_view(
            manager=self,
            group_class=self.group_class,
            model=self.membership_class,
            *args, **kwargs
        )

    def update_view(self, *args, **kwargs):
        return GroupUpdateView.as_view(
            manager=self,
            model=self.group_class,
            fields=['slug', 'name', 'state'] + self.update_fields,
            *args, **kwargs
        )

    def membership_update_view(self, *args, **kwargs):
        return GroupMembershipFormView.as_view(
            manager=self,
            model=self.group_class,
            membership_class=self.membership_class,
            *args, **kwargs
        )

    # We need to put the function view inside the class based view because values are set at runtime
    def invite_view(self, *args, **kwargs):
        """
        Initiates the organization and user account creation process
        """
        from aristotle_mdr.contrib.user_management.org_backends import InviteView as InviteViewBase

        class InviteView(HasRolePermissionMixin, InviteViewBase, GroupMixin):
            role_permission = "invite_member"
            success_url = "aristotle-user:registry_user_list"
            template_name = "aristotle_mdr/users_management/invite_user_to_registry.html"

            def form_valid(self, form):
                """
                If the form is valid, redirect to the supplied URL.
                """
                self.invited_users = form.emails
                self.manager.invite_by_emails(form.emails, request=self.request, group=self.get_group())

                return HttpResponseRedirect(self.get_success_url())

            def get_success_url(self):
                messages.success(
                    self.request,
                    _(
                        '%(count)s users invited. Once they have accepted their invitations they will appear in the members list below.'
                    ) % {
                        "count": len(self.invited_users)
                    }
                )
                # TODO: You will recieve a notification when they have accepted their invitation.

                return reverse(
                    "%s:%s" % (self.manager.namespace, "member_list"),
                    args=[self.group.slug]
                )

        return InviteView.as_view(manager=self, group_class=self.group_class)

    # TODO: These will need to be updated

    notification_subject = 'aristotle_mdr/users_management/newuser/email/notification_subject.txt'
    notification_body = 'aristotle_mdr/users_management/newuser/email/notification_body.html'

    invitation_subject = 'aristotle_mdr/users_management/newuser/email/invitation_subject.txt'
    invitation_body = 'aristotle_mdr/users_management/newuser/email/invitation_body.html'
    reminder_subject = 'aristotle_mdr/users_management/newuser/email/reminder_subject.txt'
    reminder_body = 'aristotle_mdr/users_management/newuser/email/reminder_body.html'

    registration_form_template = 'aristotle_mdr/users_management/newuser/register_form.html'
    accept_url_name = 'registry_invitations_register'

    def activate_view(self):
        """
        View function that activates the given User by setting `is_active` to
        true if the provided information is verified.
        """
        from aristotle_mdr.contrib.user_management.forms import UserRegistrationForm

        class ActivateView(GroupMixin, UpdateView):
            form_class = UserRegistrationForm
            template_name = 'groups/newuser/register_form.html'
            model = User

            def get_template_names(self):
                user = self.get_object()
                if user.is_active:
                    template_name = 'groups/accept_invite.html'
                else:
                    template_name = 'groups/newuser/register_form.html'
                return template_name

            def get_form_class(self):
                user = self.get_object()
                if user.is_active:
                    class ActivateMembershipForm(forms.ModelForm):
                        class Meta:
                            fields = []
                            model = User

                    return ActivateMembershipForm
                else:
                    return UserRegistrationForm

            def get_object(self, queryset=None):
                try:
                    user = User.objects.get(id=self.kwargs['user_id'])  # , is_active=False)
                except User.DoesNotExist:
                    raise Http404(_("Your URL may have expired."))
                if not GroupRegistrationTokenGenerator(self.get_group()).check_token(user, self.kwargs['token']):
                    raise Http404(_("Your URL may have expired."))
                if user.is_active and user.pk != self.request.user.pk:
                    raise Http404(_("Your have someone elses invitation."))

                self.invited_user = user
                return self.invited_user

            def form_valid(self, form):
                user = self.get_object()
                if not user.is_active:
                    form.instance.is_active = True
                    user = form.save()
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                self.get_group().grant_role(role=self.get_group().new_member_role, user=user)
                return redirect(self.get_success_url())

            def get_success_url(self):
                return reverse(
                    "%s:%s" % (self.manager.namespace, "member_list"),
                    args=[self.group.slug]
                )

        return ActivateView.as_view(manager=self, group_class=self.group_class)

    def invite_by_emails(self, emails, group, sender=None, request=None, **kwargs):
        """Creates an inactive user with the information we know and then sends
        an invitation email for that user to complete registration.
        If your project uses email in a different way then you should make to
        extend this method as it only checks the `email` attribute for Users.

        We'll still send an email if the user exists
        """
        users = []
        for email in emails:
            try:
                user = User.objects.get(email=email)
                # We still want to send an invitation link
                logger.debug("The user exists")

            except User.DoesNotExist:
                # TODO break out user creation process
                user = User.objects.create(
                    email=email,
                    password=get_user_model().objects.make_random_password()
                )
                user.is_active = False
                user.save()
            self.send_invitation(user, group=group, sender=request.user, request=request, **kwargs)
            users.append(user)
        return users

    def email_message(self, user, subject_template, body_template, request, group, sender=None,
                      message_class=EmailMessage, **kwargs):
        """
        Returns an email message for a new user.

        This can be easily overriden.
        For instance, to send an HTML message, use the EmailMultiAlternatives message_class
        and attach the additional component.
        """

        if sender:
            # We have a specific sender
            import email.utils
            from_email = "%s <%s>" % (
                sender.full_name,
                email.utils.parseaddr(settings.DEFAULT_FROM_EMAIL)[1]
            )
            reply_to = "%s <%s>" % (sender.full_name, sender.email)
        else:
            # There's no specific sender
            from_email = settings.DEFAULT_FROM_EMAIL
            reply_to = from_email

        headers = {'Reply-To': reply_to}
        kwargs.update({
            'sender': sender,
            'user': user,
            'accept_url': reverse(
                "%s:%s" % (self.namespace, "accept_invitation"),
                args=[group.slug, user.pk, self.get_token(user, group)],
            ),
            'request': request
        })

        subject_template = loader.get_template(subject_template)
        body_template = loader.get_template(body_template)
        subject = subject_template.render(kwargs).strip()  # Remove stray newline characters
        body = body_template.render(kwargs)

        return message_class(subject, body, from_email, [user.email], headers=headers)

    def send_invitation(self, user, group, sender=None, **kwargs):
        """An intermediary function for sending an invitation email that
        selects the templates, generating the token, and ensuring that the user
        has not already joined the site.

        We're currently not sending emails to users already part of the registry
         because we're using a different View to add users
        to Stewardship Organisations for the time being.
        """
        if user.is_active:
            return False

        token = self.get_token(user, group)
        kwargs.update({'token': token})
        kwargs.update({'sender': sender})
        kwargs.update({'user_id': user.pk})
        # Send the email
        self.email_message(user, self.invitation_subject, self.invitation_body, group=group, **kwargs).send()
        return True

    def get_token(self, user, group, **kwargs):
        """Returns a unique token for the given user"""
        return GroupRegistrationTokenGenerator(group).make_token(user)


def group_backend_factory(*args, **kwargs):
    return GroupURLManager(*args, **kwargs)
