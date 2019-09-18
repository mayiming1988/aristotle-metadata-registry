from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.groups.backends import GroupMixin
from collections import Counter


class StewardGroupMixin(GroupMixin):
    group_class = MDR.StewardOrganisation


def get_aggregate_count_of_collection(queryset):
    """ Return a dict with the count of each item type in a queryset of concepts """
    types = []

    for item in queryset:
        types.append(item.item_type)

    return dict(Counter(types))
