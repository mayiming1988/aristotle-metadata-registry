from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from django.conf.urls import url
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import (
    FormView, ListView,
    DetailView,
    UpdateView,
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

import logging
logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

class ListForObjectMixin(DetailView):
    related_class = None
    def get_object(self):
        self.object = DetailView.get_object(self, queryset=self.related_class.objects.all())
        return self.object

class GroupMixin(object):
    manager = None
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.group_list_for_user(self.request.user).prefetch_related('members')


class GroupMemberMixin(object):
    manager = None
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(group=self.get_object())


class HasRoleMixin(PermissionRequiredMixin):
    role = None
    # def has_role:
        
    def check_permissions(self, request):
        assert self.role != None
        self.object = self.get_object()
        return self.object.has_role(request.user, self.role)

class HasRolePermissionMixin(PermissionRequiredMixin):
    role_permission = None
    # def has_role:
        
    def check_permissions(self, request):
        assert self.role_permission != None
        self.object = self.get_object()
        roles = self.object.role_permissions[self.role_permission]
        return self.object.has_role(roles, request.user)


class GroupListView(LoginRequiredMixin, GroupMixin, ListView):
    template_name = "groups/group/list.html"


class GroupMemberListView(LoginRequiredMixin, HasRolePermissionMixin, GroupMemberMixin, ListView, ListForObjectMixin):
    template_name = "groups/group/change_members.html"
    role_permission = "edit_members"


class GroupDetailView(LoginRequiredMixin, GroupMixin, DetailView):
    template_name = "groups/group/detail.html"


class GroupUpdateView(LoginRequiredMixin, HasRolePermissionMixin, GroupMixin, UpdateView):
    template_name = "groups/group/update.html"
    role_permission = "edit_group"

    def get_success_url(self):
        return reverse("%s:%s"%(self.manager.namespace,"detail"), args=[self.object.slug])


@attr.s
class GroupURLManager(object):
    """
    A backend for allowing new users to join the site by creating a new user
    associated with a new organization.
    """
    group_class = attr.ib()
    membership_class = attr.ib()
    url_path = attr.ib()
    namespace = attr.ib()
    update_fields = attr.ib(default=['slug', 'name'])

    # form_class = forms.AristotleUserRegistrationForm

    def group_meta(self):
        return self.group_class._meta

    def get_success_url(self):
        return reverse('friendly_login') + '?welcome=true'

    def get_urls(self):
        item_path = r'^/(?P<slug>[-\w]+)/$'.format(url_path=self.url_path)
        item_update_path = r'^/(?P<slug>[-\w]+)/edit/$'.format(url_path=self.url_path)
        member_details_path = r'^/(?P<slug>[-\w]+)/members/$'.format(url_path=self.url_path)
        
        return [
            url(r'^/?$', view=self.list_view(), name="list"),
            url(item_path, view=self.detail_view(), name="detail"),
            url(item_update_path, view=self.update_view(), name="update"),
            url(member_details_path, view=self.member_list_view(), name="member_list"),
            #     view=self.activate_view, name="list"),
            # url(r'^accept/(?P<user_id>[\d]+)-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            #     view=self.activate_view, name="list"),
            # url(r'^$', view=self.invite_view(), name="registry_invitations_create"),
        ]

    def list_view(self, *args, **kwargs):
        return GroupListView.as_view(manager=self, model=self.group_class, *args, **kwargs)

    def detail_view(self, *args, **kwargs):
        return GroupDetailView.as_view(manager=self, model=self.group_class, *args, **kwargs)

    def member_list_view(self, *args, **kwargs):
        return GroupMemberListView.as_view(
            manager=self,
            related_class=self.group_class,
            model=self.membership_class,
            *args, **kwargs
        )

    def update_view(self, *args, **kwargs):
        return GroupUpdateView.as_view(
            manager=self,
            model=self.group_class,
            fields=self.update_fields,
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
