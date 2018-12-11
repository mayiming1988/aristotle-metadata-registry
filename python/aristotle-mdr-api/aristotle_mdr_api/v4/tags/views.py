from rest_framework import generics
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit
from aristotle_mdr_api.v4.tags import serializers
from django.shortcuts import get_object_or_404

from aristotle_mdr.contrib.favourites.models import Tag, Favourite
from aristotle_mdr.models import _concept


class TagView(generics.RetrieveUpdateDestroyAPIView):
    """Retrive and update and issue"""
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.TagSerializer
    queryset=Tag.objects.all()


class ItemTagUpdateView(generics.UpdateAPIView):
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.ItemTagSerializer
    pk_url_kwarg='iid'

    def dispatch(self, request, *args, **kwargs):
        item_id = self.kwargs[self.pk_url_kwarg]
        self.item = get_object_or_404(_concept, pk=item_id)
        return super().dispatch(request, *args, *kwargs)

    def get_object(self):
        self.check_object_permissions(self.request, self.item)
        return Favourite.objects.filter(
            tag__profile=self.request.user.profile,
            tag__primary=False,
            item=self.item
        ).select_related('tag')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['item'] = self.item
        return context
