from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.groups.backends import GroupMixin


class StewardGroupMixin(GroupMixin):
    group_class = MDR.StewardOrganisation


def get_aggregate_count_of_collection(queryset):
    item_to_count = {}

    for item in queryset:
        item_to_count[item.item_type] += 1

    return item_to_count



