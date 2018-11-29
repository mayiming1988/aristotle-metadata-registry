from rest_framework import serializers

from aristotle_mdr_api.v4.serializers import MultiUpdateListMixin
from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldListSerializer(MultiUpdateListMixin, serializers.ListSerializer):
    pass


class CustomFieldSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = CustomField
        fields = ('id', 'name', 'type', 'help_text', 'hr_type')
        read_only_fields = ('hr_type',)
        list_serializer_class = CustomFieldListSerializer
