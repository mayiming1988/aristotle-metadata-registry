from typing import Dict
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet

from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.groups.backends import GroupMixin
from collections import defaultdict

from aristotle_mdr.contrib.stewards.models import Collection


class StewardGroupMixin(GroupMixin):
    group_class = MDR.StewardOrganisation


def get_aggregate_count_of_collection(queryset: QuerySet,
                                      sub_collection_count: int = None) -> Dict[ContentType, int]:
    """Return a dict with the count of each item type in a queryset of concepts"""

    counts: Dict[ContentType, int] = defaultdict(int)
    for item in queryset:
        counts[item.item_type] += 1

    if sub_collection_count is not None:
        counts[ContentType.objects.get_for_model(Collection)] = sub_collection_count

    # We want to convert back to dict here
    # since you can't access .items of a defaultdict in templates
    return dict(counts)


def add_urls_to_config_list(config_list, group):
    for app in config_list:
        app['url'] = reverse('aristotle:stewards:group:browse_app_models', args=[group.slug, app['app'].label])
        for model in app['models']:
            qs = model['queryset']
            qs = qs.filter(stewardship_organisation=group)
            model['queryset'] = qs
            model['url'] = reverse(
                'aristotle:stewards:group:browse_app_metadata',
                args=[group.slug, model['content_type'].app_label, model['content_type'].model]
            )
    return config_list
