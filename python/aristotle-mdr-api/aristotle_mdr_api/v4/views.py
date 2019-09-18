from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from aristotle_mdr.models import _concept
from aristotle_mdr import perms


class ObjectAPIView(APIView):
    """API View providing a util function to get an item with permission checks"""

    # Model to lookup, default to _concept
    model = _concept
    # Url kwarg containing the primary key
    pk_url_kwarg = 'pk'

    def get_object(self):
        id = self.kwargs[self.pk_url_kwarg]
        obj = get_object_or_404(self.model, pk=id).item
        if not perms.user_can_view(self.request.user, obj):
            raise PermissionDenied
        return obj
