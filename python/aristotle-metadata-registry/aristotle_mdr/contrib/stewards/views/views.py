from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q
from django.views.generic import ListView

from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.views.utils import SortedListView

import logging
logger = logging.getLogger(__name__)


class BrowseStewardOrganisationView(ListView):
    template_name = 'aristotle_mdr/stewards/browse_stewards.html'

    def get_queryset(self):
        return StewardOrganisation.objects.visible(self.request.user)


class RegistryAdministratorPermissionsMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = "aristotle_mdr.is_registry_administrator"
    redirect_unauthenticated_users = True
    raise_exception = True


class StewardOrganisationListBase(SortedListView):
    paginate_by = 20
    model = StewardOrganisation

    def get_initial_queryset(self):
        raise NotImplementedError

    def get_queryset(self):
        qs = self.get_initial_queryset()

        metadata_counts = dict(qs.values_list('pk').annotate(
            num_items=Count('metadata', distinct=True),
        ))
        member_counts = dict(qs.values_list('pk').annotate(
            num_members=Count('members', distinct=True),
        ))
        workgroup_counts = dict(qs.values_list('pk').annotate(
            num_members=Count('workgroup', distinct=True),
        ))
        # This is very inefficient when member, workgroup and metadata counts grow
        groups = qs.annotate(
            num_ras=Count('registrationauthority', distinct=True),
        )

        if self.text_filter:
            groups = groups.filter(Q(name__icontains=self.text_filter) | Q(definition__icontains=self.text_filter))

        groups = self.sort_queryset(groups)
        for group in groups:
            group.num_items = metadata_counts[group.pk]
            group.num_members = member_counts[group.pk]
            group.num_workgroups = workgroup_counts[group.pk]

        return groups


class ListAllStewardOrganisationsView(RegistryAdministratorPermissionsMixin, StewardOrganisationListBase):
    template_name = "aristotle_mdr/user/organisations/list_all.html"

    def get_initial_queryset(self):
        return StewardOrganisation.objects.all()


class ListOwnStewardOrganisationsView(StewardOrganisationListBase, LoginRequiredMixin):
    template_name = 'aristotle_mdr/stewardorganisation_list.html'

    def get_initial_queryset(self):
        return StewardOrganisation.objects.group_list_for_user(self.request.user)
