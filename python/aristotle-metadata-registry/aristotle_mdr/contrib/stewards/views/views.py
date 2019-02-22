from braces.views import LoginRequiredMixin, PermissionRequiredMixin
# from aristotle_mdr.contrib.stewards import models
from django.db.models import Count, Q, Model
from django.views.generic import (
    CreateView,
)
from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.views.utils import (
    SortedListView
)
from aristotle_mdr.contrib.groups.backends import GroupBase


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
        groups = self.get_initial_queryset().annotate(
            num_items=Count('metadata', distinct=True),
            num_workgroups=Count('workgroup', distinct=True),
            num_ras=Count('registrationauthority', distinct=True),
            num_members=Count('members', distinct=True)
        )

        if self.text_filter:
            groups = groups.filter(Q(name__icontains=self.text_filter) | Q(definition__icontains=self.text_filter))

        groups = self.sort_queryset(groups)
        return groups
