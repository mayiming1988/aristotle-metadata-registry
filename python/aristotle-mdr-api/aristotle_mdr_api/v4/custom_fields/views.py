from rest_framework import generics
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit

from aristotle_mdr.contrib.custom_fields.models import CustomField
from aristotle_mdr_api.v4.custom_fields import serializers


class CustomFieldRetrieveView(generics.RetrieveAPIView):
    """Retrieve Custom Field"""
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.CustomFieldSerializer
    queryset=CustomField.objects.all()
