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

from aristotle_mdr.views.utils import UserFormViewMixin

from aristotle_mdr.contrib.stewards.models import Collection
from aristotle_mdr.contrib.stewards.forms import CollectionForm

from aristotle_mdr.contrib.groups.backends import (
    GroupURLManager, GroupMixin,
    HasRoleMixin, HasRolePermissionMixin,
)

import logging

logger = logging.getLogger(__name__)


class EditCollectionViewBase(UserFormViewMixin, GroupMixin, HasRolePermissionMixin):
    model = Collection
    form_class = CollectionForm
    current_group_context = "collections"
    role_permission = "manage_collections"

    def form_valid(self, form):
        form.instance.stewardship_organisation = self.get_group()
        return super().form_valid(form)
