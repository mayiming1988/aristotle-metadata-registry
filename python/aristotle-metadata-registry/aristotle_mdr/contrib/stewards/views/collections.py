from aristotle_mdr.views.utils import UserFormViewMixin

from aristotle_mdr.contrib.stewards.models import Collection
from aristotle_mdr.contrib.stewards.forms.collections import CollectionForm

from aristotle_mdr.contrib.groups.backends import GroupMixin, HasRolePermissionMixin

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

    def get_queryset(self):
        return self.get_group().collection_set.all().visible(self.request.user)
