from django import template


register = template.Library()


@register.simple_tag()
def user_has_role(group, user, role):
    try:
        return group.has_role(role=role, user=user)
    except Exception as e:
        return False


@register.simple_tag()
def user_has_role_permission(group, user, role_perm):
    try:
        return group.user_has_permission(permission=role_perm, user=user)
    except Exception as e:
        return False
