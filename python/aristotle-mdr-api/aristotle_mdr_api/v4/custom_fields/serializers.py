from rest_framework import serializers

from aristotle_mdr_api.v4.serializers import MultiUpdateNoDeleteListSerializer
from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    order = serializers.IntegerField()
    name = serializers.CharField(max_length=1000)
    choices = serializers.CharField(allow_blank=True, default='')
    system_name = serializers.CharField(validators=[])

    def get_system_name(self, obj):
        if obj.system_name is None:
            return ''
        return obj.system_name.split(':', 1)[-1]

    def create(self, validated_data):
        raise ValueError(validated_data)

    def update(self, instance, validated_data):
        raise ValueError(validated_data)

    class Meta:
        model = CustomField
        fields = ('id', 'order', 'name', 'type', 'system_name', 'help_text', 'help_text_long', 'hr_type',
                  'allowed_model', 'visibility', 'hr_visibility', 'state', 'choices')
        read_only_fields = ('hr_type', 'hr_visibility')

        list_serializer_class = MultiUpdateNoDeleteListSerializer
