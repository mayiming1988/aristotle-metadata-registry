from django.urls import reverse

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
