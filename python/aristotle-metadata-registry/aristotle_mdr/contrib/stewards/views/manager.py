from braces.views import LoginRequiredMixin, PermissionRequiredMixin


from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, CreateView
from django.db.models import Q

from django.conf.urls import url

from aristotle_mdr.contrib.groups.backends import (
    GroupURLManager, GroupMixin,
    IsGroupMemberMixin, HasRoleMixin,
    HasRolePermissionMixin,
)
# from aristotle_mdr.models import StewardOrganisationMembership, StewardOrganisation, _concept
from aristotle_mdr import models as MDR
from aristotle_mdr.views.workgroups import GenericListWorkgroup, CreateWorkgroup
from aristotle_mdr.views.registrationauthority import ListRegistrationAuthority
from . import views

class StewardURLManager(GroupURLManager):
    group_context_name = "stewardship_organisation"

    def get_extra_group_urls(self):
        return [
            url("browse", view=self.browse_view(), name="browse"),
            url("workgroups/$", view=self.workgroup_list_view(), name="workgroups"),
            url("workgroups/create/$", view=self.workgroup_create_view(), name="workgroups_create"),
            url("managed_items/create/(?P<model_name>.+)/?$", view=self.managed_item_create_view(), name="create_managed_item"),
            # url("managed_items/(?P<model_name>.+)/(?P<pk>.+)?$", view=self.managed_item_view(), name="create_managed_item"),
            url("ras/$", view=self.registration_authority_list_view(), name="registrationauthorities"),
        ]

    def list_all_view(self, *args, **kwargs):
        return views.ListStewardOrg.as_view(manager=self, model=self.group_class, *args, **kwargs)

    def workgroup_list_view(self):
        class ListWorkgroup(GroupMixin, IsGroupMemberMixin, GenericListWorkgroup):
            role_permission = "list_workgroups"
            template_name = "aristotle_mdr/user/workgroups/steward_list.html"
            raise_exception = True
        
            def get_initial_queryset(self):
                return self.get_group().workgroup_set.all()
        return ListWorkgroup.as_view(manager=self, group_class=self.group_class)

    def workgroup_create_view(self):
        from aristotle_mdr.views.workgroups import CreateWorkgroup as Base
        class CreateWorkgroup(HasRolePermissionMixin, GroupMixin, Base):
            role_permission = "manage_workgroups"

            def get_initial(self):
                initial = super().get_initial()
                initial['stewardship_organisation'] = self.get_group()
                return initial

        return CreateWorkgroup.as_view(manager=self, group_class=self.group_class)

    def registration_authority_list_view(self):
        class ListRegistrationAuthorities(GroupMixin, IsGroupMemberMixin, ListRegistrationAuthority):
            role_permission = "list_registrationauthorities"
            template_name = "aristotle_mdr/user/registration_authority/steward_list.html"
            raise_exception = True
        
            def get_queryset(self):
                return self.get_group().registrationauthority_set.all()
        return ListRegistrationAuthorities.as_view(manager=self, group_class=self.group_class)

    def browse_view(self):
        from aristotle_mdr.contrib.browse.views import BrowseConcepts
        class Browse(GroupMixin, BrowseConcepts):
            model = MDR._concept

            def get_queryset(self, *args, **kwargs):
                qs = super().get_queryset(*args, **kwargs)
                return qs.filter(stewardship_organisation=self.get_group())
            def get_context_data(self, *args, **kwargs):
                # Call the base implementation first to get a context
                self.kwargs['app'] = "aristotle_mdr"
                context = super().get_context_data(*args, **kwargs)
                # if self.kwargs['app'] not in fetch_metadata_apps():
                #     raise Http404
                # context['app_label'] = self.kwargs['app']
                # context['app'] = apps.get_app_config(self.kwargs['app'])
                return context
            def get_template_names(self):
                return ['stewards/metadata/list.html']
        return Browse.as_view(manager=self, group_class=self.group_class)
    
    def managed_item_create_view(self):
        from django.contrib.contenttypes.models import ContentType
        class CreateManagedItemView(GroupMixin, CreateView):
            template_name = "stewards/managed_item/add.html"
            fields=["stewardship_organisation", "name", "definition"]

            def dispatch(self, request, *args, **kwargs):
                model_name = self.kwargs.get("model_name").lower()
                self.model = ContentType.objects.get(model=model_name).model_class()
                return super().dispatch(request, *args, **kwargs)

            def get_context_data(self, **kwargs):
                kwargs.update({
                    "model": self.model,
                    "model_name": self.model._meta.verbose_name.title(),
                })
                return super().get_context_data(**kwargs)

            def get_initial(self):
                initial = super().get_initial()
                initial['stewardship_organisation'] = self.get_group()
                return initial

        return CreateManagedItemView.as_view(manager=self, group_class=self.group_class)


def group_backend_factory(*args, **kwargs):
    kwargs.update(dict(
                group_class = MDR.StewardOrganisation,
                membership_class = MDR.StewardOrganisationMembership,
                namespace="aristotle_mdr:stewards:group",
    ))
    
    return StewardURLManager(*args, **kwargs)

# class RegistryOwnerUserList(LoginRequiredMixin, PermissionRequiredMixin, ListView):
#     template_name='aristotle_mdr/users_management/users/list.html'

#     permission_required = "aristotle_mdr.list_registry_users"
#     raise_exception = True
#     redirect_unauthenticated_users = True

#     def get_queryset(self):
#         q = self.request.GET.get('q', None)
#         queryset = get_user_model().objects.all().order_by(
#             '-is_active', 'full_name', 'short_name', 'email'
#         )
#         if q:
#             queryset = queryset.filter(
#                 Q(short_name__icontains=q) |
#                 Q(full_name__icontains=q) |
#                 Q(email__icontains=q)
#             )
#         return queryset


# class DeactivateRegistryUser(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
#     template_name='aristotle_mdr/users_management/users/deactivate.html'

#     permission_required = "aristotle_mdr.deactivate_registry_users"
#     raise_exception = True
#     redirect_unauthenticated_users = True

#     http_method_names = ['get', 'post']

#     def post(self, request, *args, **kwargs):
#         deactivated_user = self.kwargs.get('user_pk')
#         deactivated_user = get_object_or_404(get_user_model(), pk=deactivated_user)
#         deactivated_user.is_active = False
#         deactivated_user.save()
#         return redirect(reverse("aristotle-user:registry_user_list"))

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         deactivate_user = self.kwargs.get('user_pk')
#         if not deactivate_user:
#             raise Http404

#         deactivate_user = get_object_or_404(get_user_model(), pk=deactivate_user)

#         data['deactivate_user'] = deactivate_user
#         return data


# class ReactivateRegistryUser(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
#     template_name='aristotle_mdr/users_management/users/reactivate.html'

#     permission_required = "aristotle_mdr.reactivate_registry_users"
#     raise_exception = True
#     redirect_unauthenticated_users = True

#     http_method_names = ['get', 'post']

#     def post(self, request, *args, **kwargs):
#         reactivated_user = self.kwargs.get('user_pk')
#         reactivated_user = get_object_or_404(get_user_model(), pk=reactivated_user)
#         reactivated_user.is_active = True
#         reactivated_user.save()
#         return redirect(reverse("aristotle-user:registry_user_list"))

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         reactivate_user = self.kwargs.get('user_pk')
#         if not reactivate_user:
#             raise Http404

#         reactivate_user = get_object_or_404(get_user_model(), pk=reactivate_user)

#         data['reactivate_user'] = reactivate_user
#         return data
