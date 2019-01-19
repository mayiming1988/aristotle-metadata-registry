from braces.views import (
    LoginRequiredMixin, PermissionRequiredMixin, SuperuserRequiredMixin
)

import os

from django import forms
from django.conf.urls import url, include
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (
    FormView,
    ListView,
    DetailView,
    UpdateView,
    CreateView,
    RedirectView,
)
from django.template import loader

# from organizations.backends.defaults import InvitationBackend
# from organizations.backends.tokens import RegistrationTokenGenerator

# from . import forms
import attr

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage
from django.utils.translation import ugettext_lazy as _

from django.http import Http404

from .base import AbstractGroup

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
    fallback_template_name = None

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
        logger.critical(templates)
        return templates


class GroupBase(GroupTemplateMixin):
    manager = None
    slug_url_kwarg = "group_slug"
    group_class = AbstractGroup
    group_slug_url_kwarg = "group_slug"
    superuser_override = True
    group_context_name = None

    def get_group_queryset(self):
        if hasattr(self, 'model') and issubclass(self.model, AbstractGroup):
            qs = super().get_queryset()
        else:
            qs = self.group_class.objects.all()
        qs = qs.prefetch_related('members')
        if self.request.user.is_anonymous():
            return qs
        # if self.superuser_override and self.request.user.is_superuser:
        #     return qs.prefetch_related('members')
        return qs.group_list_for_user(self.request.user).prefetch_related('members')


class GroupMixin(GroupBase):
    def get_group_context_name(self):
        for obj in [self, self.manager]:
            name = getattr(obj, "group_context_name")
            if name is not None:
                return name
        return "group"

    def get_group(self):
        if hasattr(self, 'model') and issubclass(self.model, AbstractGroup):
            slug = self.slug_url_kwarg
        else:
            slug = self.group_slug_url_kwarg
        return get_object_or_404(
            self.get_group_queryset(), slug=self.kwargs[slug]
        )

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context.update({self.get_group_context_name(): self.get_group()})
        context.update({"group": self.get_group()})
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
        assert self.role != None
        self.group = self.get_group()
        return self.group.has_role(request.user, self.role)


class HasRolePermissionMixin(PermissionRequiredMixin):
    role_permission = None
    raise_exception = True
    redirect_unauthenticated_users = True

    def check_permissions(self, request):
        assert self.role_permission != None
        self.group = self.get_group()
        can_access = self.group.user_has_permission(user=request.user, permission=self.role_permission)
        logger.critical(["user can access", can_access])
        return can_access


class GroupListView(LoginRequiredMixin, GroupBase, ListView):
    fallback_template_name = "groups/group/list.html"
    superuser_override = False

    def get_queryset(self):
        return super().get_group_queryset()


class GroupListAllView(SuperuserRequiredMixin, GroupListView):
    fallback_template_name = "groups/group/list.html"
    superuser_override = True


class GroupMemberListView(LoginRequiredMixin, HasRolePermissionMixin, GroupMixin, ListView): #, ListForObjectMixin):
    fallback_template_name = "groups/group/members/list.html"
    role_permission = "edit_members"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(group=self.get_group())


class GroupMemberAddView(LoginRequiredMixin, HasRolePermissionMixin, GroupMixin, CreateView):
    fallback_template_name = "groups/group/members/add.html"
    role_permission = "edit_members"
    # queryset = User.objects.all()
    fields = ["user", "role"]

    def form_valid(self, form):
        form.instance.group = self.get_group()
        return super().form_valid(form)

    def get_initial(self):
        initial = self.initial.copy()
        initial.update({"group": self.get_group()})
        return initial

    def get_success_url(self):
        return reverse("%s:%s"%(self.manager.namespace,"detail"), args=[self.group.slug])


class GroupMemberRemoveView(LoginRequiredMixin, HasRolePermissionMixin, GroupMemberMixin, FormView):
    fallback_template_name = "groups/group/members/remove.html"
    role_permission = "edit_members"
    form_class = forms.Form  # We literally just need a blank form

    def form_valid(self, form):
        self.get_group().members.filter(
            user = self.kwargs['member_pk']   
        ).delete()
        
        return HttpResponseRedirect(
            reverse("%s:%s"%(self.manager.namespace,"detail"), args=[self.group.slug])
        )
        

class GroupDetailView(HasRolePermissionMixin, GroupMixin, DetailView):
    fallback_template_name = "groups/group/detail.html"
    role_permission = "view_group"


class GroupCreateView(LoginRequiredMixin, PermissionRequiredMixin, GroupBase, CreateView):
    fallback_template_name = "groups/group/create.html"
    role_permission = "edit_group_details"
    # permission = "create_group_details"
    manager = None
    fields = ['name', 'description']

    def get_permission_required(self, request=None):
        perm = "{}.add_{}".format(
            self.manager.group_class._meta.app_label,
            self.manager.group_class._meta.model_name,
        )
        logger.critical(perm)
        return perm


    # def get_object(self):
    #     return self.manager.group_class

    def get_success_url(self):
        return reverse("%s:%s"%(self.manager.namespace,"detail"), args=[self.object.slug])


class GroupUpdateView(LoginRequiredMixin, HasRolePermissionMixin, GroupMixin, UpdateView):
    fallback_template_name = "groups/group/update.html"
    role_permission = "edit_group_details"

    def get_success_url(self):
        return reverse("%s:%s"%(self.manager.namespace,"detail"), args=[self.object.slug])


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
        return reverse("%s:%s"%(self.manager.namespace,"member_list"), args=[self.group.slug])

    def form_valid(self, form):
        self.get_group().grant_role(form.cleaned_data['role'], user=self.get_member())
        return super().form_valid(form)


@attr.s
class GroupURLManager(object):
    """
    A backend for allowing new users to join the site by creating a new user
    associated with a new organization.
    """
    group_class = attr.ib()
    membership_class = attr.ib()
    url_path = "" #attr.ib(default="")
    namespace = attr.ib()
    update_fields = attr.ib(default=[])
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
            url(r'^/?$', view=RedirectView.as_view(pattern_name=self.namespace+":list")),
            url(r'^s/create/$', view=self.create_view(), name="create"),
            url(r'^s/all/$', view=self.list_all_view(), name="list_all"),

            url("^/(?P<group_slug>[-\w]+)/", include([
                url("^$", view=self.detail_view(), name="detail"),
                url("edit", view=self.update_view(), name="update"),
                url("", include(self.get_extra_group_urls()))
            ])),
            url("^/(?P<group_slug>[-\w]+)/members/", include([
                url(r'^$', view=self.membership_list_view(), name="member_list"),
                url(r'^add$', view=self.membership_add_view(), name="member_add"),
                url(r'^(?P<member_pk>[\d]+)/?$', view=self.membership_update_view(), name="membership_update"),
                url(r'^(?P<member_pk>[\d]+)/remove', view=self.membership_remove_view(), name="membership_remove"),
            ]))

            #     view=self.activate_view, name="list"),
            # url(r'^accept/(?P<user_id>[\d]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            #     view=self.activate_view, name="list"),
            # url(r'^$', view=self.invite_view(), name="registry_invitations_create"),
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


        # class kls(GroupListView):
            
        # print(*args, **kwargs)
        # return kls.as_view(*args, **kwargs)
    
    # def invite_view(self):
    #     """
    #     Initiates the organization and user account creation process
    #     """
    #     return InviteView.as_view(backend=self)

    # def activate_view(self, request, user_id, token):
    #     """
    #     View function that activates the given User by setting `is_active` to
    #     true if the provided information is verified.
    #     """
    #     try:
    #         user = self.user_model.objects.get(id=user_id, is_active=False)
    #     except self.user_model.DoesNotExist:
    #         raise Http404(_("Your URL may have expired."))
    #     if not RegistrationTokenGenerator().check_token(user, token):
    #         raise Http404(_("Your URL may have expired."))

    #     form = self.get_form(data=request.POST or None, instance=user)
    #     if form.is_valid():
    #         form.instance.is_active = True
    #         user = form.save()
    #         user.set_password(form.cleaned_data['password'])
    #         user.save()
    #         self.activate_organizations(user)
    #         return redirect(self.get_success_url())
    #     return render(request, self.registration_form_template, {'form': form})

    # def invite_by_emails(self, emails, sender=None, request=None, **kwargs):
    #     """Creates an inactive user with the information we know and then sends
    #     an invitation email for that user to complete registration.
    #     If your project uses email in a different way then you should make to
    #     extend this method as it only checks the `email` attribute for Users.
    #     """
    #     User = get_user_model()
    #     users = []
    #     for email in emails:
    #         try:
    #             user = User.objects.get(email=email)
    #         except User.DoesNotExist:
    #             # TODO break out user creation process
    #             user = User.objects.create(
    #                 email=email,
    #                 password=get_user_model().objects.make_random_password()
    #             )
    #             user.is_active = False
    #             user.save()
    #         self.send_invitation(user, sender, request=request, **kwargs)
    #         users.append(user)
    #     return users

    # def email_message(self, user, subject_template, body_template, request, sender=None, message_class=EmailMessage, **kwargs):
    #     """
    #     Returns an email message for a new user. This can be easily overriden.
    #     For instance, to send an HTML message, use the EmailMultiAlternatives message_class
    #     and attach the additional conent.
    #     """

    #     if sender:
    #         import email.utils
    #         from_email = "%s <%s>" % (
    #             sender.full_name,
    #             email.utils.parseaddr(settings.DEFAULT_FROM_EMAIL)[1]
    #         )
    #         reply_to = "%s <%s>" % (sender.full_name, sender.email)
    #     else:
    #         from_email = settings.DEFAULT_FROM_EMAIL
    #         reply_to = from_email

    #     headers = {'Reply-To': reply_to}
    #     kwargs.update({'sender': sender, 'user': user})

    #     subject_template = loader.get_template(subject_template)
    #     body_template = loader.get_template(body_template)
    #     subject = subject_template.render(kwargs).strip()  # Remove stray newline characters
    #     body = body_template.render(kwargs)
    #     return message_class(subject, body, from_email, [user.email], headers=headers)

    # def send_invitation(self, user, sender=None, **kwargs):
    #     """An intermediary function for sending an invitation email that
    #     selects the templates, generating the token, and ensuring that the user
    #     has not already joined the site.
    #     """
    #     if user.is_active:
    #         return False
    #     token = self.get_token(user)
    #     kwargs.update({'token': token})
    #     kwargs.update({'sender': sender})
    #     kwargs.update({'user_id': user.pk})
    #     self.email_message(user, self.invitation_subject, self.invitation_body, **kwargs).send()
    #     return True

def group_backend_factory(*args, **kwargs):
    # _group_class = group_class
    # _membership_class = membership_class
    # url_path = url_path
    # class Backend(GroupBackend):
    #     group_class = _group_class
    #     membership_class = _membership_class

    return GroupURLManager(*args, **kwargs)
