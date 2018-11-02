from rest_framework import permissions
from aristotle_mdr import perms
from aristotle_mdr.models import _concept


class IssuePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            item_id = request.data.get('item', None)
            try:
                item = _concept.objects.get(id=item_id)
            except _concept.DoesNotExist:
                return True
            return perms.user_can_view(request.user, item)

        return True

    def has_object_permission(self, request, view, obj):

        return perms.user_can_view(request.user, item)
