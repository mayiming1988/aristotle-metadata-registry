from braces.views import LoginRequiredMixin, PermissionRequiredMixin
# from aristotle_mdr.contrib.stewards import models
from django.db.models import Count, Q, Model

from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.views.utils import (
    SortedListView
)


class ListStewardOrg(PermissionRequiredMixin, LoginRequiredMixin, SortedListView):
    template_name = "aristotle_mdr/user/organisations/list_all.html"
    permission_required = "aristotle_mdr.is_registry_administrator"
    raise_exception = True
    model = StewardOrganisation
    redirect_unauthenticated_users = True
    paginate_by = 20

    def get_initial_queryset(self):
        return StewardOrganisation.objects.all()

    def get_queryset(self):
        workgroups = self.get_initial_queryset().annotate(
            num_items=Count('metadata', distinct=True),
            num_workgroups=Count('workgroup', distinct=True),
            # num_ras=Count('registration_authority', distinct=True),
            num_members=Count('members', distinct=True)
        )
        # workgroups = workgroups.prefetch_related('viewers', 'managers', 'submitters', 'stewards')

        if self.text_filter:
            workgroups = workgroups.filter(Q(name__icontains=self.text_filter) | Q(definition__icontains=self.text_filter))

        workgroups = self.sort_queryset(workgroups)
        return workgroups

