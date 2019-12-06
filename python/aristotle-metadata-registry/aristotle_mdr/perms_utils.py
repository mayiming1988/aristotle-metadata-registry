from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from aristotle_mdr import perms


def get_if_user_can_view(obj_type, user, iid):
    item = get_object_or_404(obj_type, pk=iid)
    if perms.user_can_view(user, item):
        return item
    else:
        raise PermissionDenied


def get_if_user_can_edit(obj_type, user, iid):
    item = get_object_or_404(obj_type, pk=iid)
    if perms.user_can_edit(user, item):
        return item
    else:
        raise PermissionDenied


def get_if_user_can_supersede(obj_type, user, iid):
    item = get_object_or_404(obj_type, pk=iid)
    if perms.user_can_supersede(user, item):
        return item
    else:
        raise PermissionDenied
