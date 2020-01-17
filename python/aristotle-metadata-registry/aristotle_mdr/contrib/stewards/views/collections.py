from aristotle_mdr.views.utils import UserFormViewMixin
from aristotle_mdr.contrib.stewards.models import Collection
from aristotle_mdr.contrib.stewards.forms.collections import CollectionForm
from aristotle_mdr.contrib.groups.backends import GroupMixin, HasRolePermissionMixin

from django.http import HttpResponseRedirect

import logging

logger = logging.getLogger(__name__)


class CollectionMixin(UserFormViewMixin, GroupMixin, HasRolePermissionMixin):
    """Base class for collection views"""
    model = Collection
    form_class = CollectionForm
    current_group_context = "collections"
    role_permission = "manage_collections"

    def set_fields(self, obj):
        """Set object fields not in the form"""
        obj.stewardship_organisation = self.get_group()

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.set_fields(self.object)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_queryset(self):
        return self.get_group().collection_set.all().visible(self.request.user)
