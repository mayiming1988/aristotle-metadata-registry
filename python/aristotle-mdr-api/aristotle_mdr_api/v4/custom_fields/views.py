from rest_framework import generics
from rest_framework.response import Response
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit

from aristotle_mdr.contrib.custom_fields.models import CustomField
from aristotle_mdr_api.v4.custom_fields import serializers


class CustomFieldRetrieveView(generics.RetrieveAPIView):
    """Retrieve Custom Field"""
    permission_classes=(AuthCanViewEdit,)
    permission_key='metadata'
    serializer_class=serializers.CustomFieldSerializer
    queryset=CustomField.objects.all()


class CustomFieldListView(generics.ListAPIView):
    """List and update custom fields"""
    permission_classes=(AuthCanViewEdit,)
    permission_key='metadata'
    serializer_class=serializers.CustomFieldSerializer
    queryset=CustomField.objects.all()

    def update(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
