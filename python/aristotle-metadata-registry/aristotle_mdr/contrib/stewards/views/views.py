from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q, Model
from django.views.generic import (
    CreateView,
)
from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.views.utils import (
    SortedListView
)
from aristotle_mdr.contrib.groups.backends import GroupBase
import logging

logger = logging.getLogger(__name__)


class ListStewardOrg(PermissionRequiredMixin, LoginRequiredMixin, GroupBase, SortedListView):
    template_name = "aristotle_mdr/user/organisations/list_all.html"
    permission_required = "aristotle_mdr.is_registry_administrator"
    raise_exception = True
    model = StewardOrganisation
    redirect_unauthenticated_users = True
    paginate_by = 20

    def get_initial_queryset(self):
        return StewardOrganisation.objects.all()

    def get_queryset(self):
        metadata_counts=dict(self.get_initial_queryset().all().values_list('pk').annotate(
            num_items=Count('metadata', distinct=True),
        ))
        member_counts = dict(self.get_initial_queryset().all().values_list('pk').annotate(
            num_members=Count('members', distinct=True),
        ))
        workgroup_counts = dict(self.get_initial_queryset().all().values_list('pk').annotate(
            num_members=Count('workgroup', distinct=True),
        ))

        # This is very inefficient when member, workgroup and metadata counts grow
        groups = self.get_initial_queryset().annotate(
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
