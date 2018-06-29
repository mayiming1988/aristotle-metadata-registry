from django import template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

register = template.Library()

@register.assignment_tag() #takes_context=True)
def user_has_role(group, user, role):
    try:
        return group.has_role(role=role, user=user)
    except Exception as e:
        return False
