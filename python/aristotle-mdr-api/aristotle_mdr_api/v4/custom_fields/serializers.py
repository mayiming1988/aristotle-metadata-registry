from rest_framework import serializers

from aristotle_mdr_api.v4.serializers import MultiUpdateNoDeleteListSerializer
from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)
    order = serializers.IntegerField()
    name = serializers.CharField(max_length=1000)

    class Meta:
        model = CustomField
        fields = ('id', 'order', 'name', 'type', 'help_text', 'hr_type',
                  'allowed_model', 'visibility', 'hr_visibility', 'state')
        read_only_fields = ('hr_type', 'hr_visibility')
        list_serializer_class = MultiUpdateNoDeleteListSerializer
