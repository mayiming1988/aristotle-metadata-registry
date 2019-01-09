from django import template

from aristotle_mdr.contrib.links import perms

register = template.Library()


@register.filter
def can_edit_link(user, link):
    return perms.user_can_change_link(user, link)
