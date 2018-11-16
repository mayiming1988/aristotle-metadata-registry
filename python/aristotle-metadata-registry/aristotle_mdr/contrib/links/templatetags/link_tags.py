from django import template

from aristotle_mdr.contrib.links.models import Link
from aristotle_mdr.contrib.links import perms

register = template.Library()


@register.filter
def get_links(item):
    return Link.objects.filter(root_item=item)


@register.filter
def can_edit_link(user, link):
    return perms.user_can_change_link(user, link)
