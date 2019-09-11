from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from typing import Dict, Any

from aristotle_mdr_api.v4.serializers import MultiUpdateNoDeleteListSerializer
from aristotle_mdr.contrib.custom_fields.models import CustomField


class BulkUniqueTogetherValidator(UniqueTogetherValidator):
    """This is a workaround because DRF cannot handle bulk updates and unique_together constraints"""
    def exclude_current_instance(self, attrs, queryset):
        if attrs.get("id"):
            return queryset.exclude(pk=attrs['id'])
        return queryset


class CustomFieldSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    order = serializers.IntegerField()
    name = serializers.CharField(max_length=1000)
    choices = serializers.CharField(allow_blank=True, default='')

    def validate(self, data) -> Dict[Any, Any]:
        if CustomField.objects.filter(unique_name=data['unique_name'], allowed_model=None).count() > 0:
            raise serializers.ValidationError("A Custom Field for all models already exists!")

        if 'allowed_model' not in data:
            # It's all
            unique_names = CustomField.objects.all().values_list('unique_name', flat=True)
            if data['unique_name'] in unique_names:
                raise serializers.ValidationError("A Custom Field's unique name applying to all objects must be"
                                                  "globally unique")
        return data

    def get_unique_together_validators(self):
        return [BulkUniqueTogetherValidator(queryset=CustomField.objects.all(),
                                            fields=('allowed_model', 'unique_name'))]

    class Meta:
        model = CustomField
        fields = ('id', 'order', 'name', 'type', 'help_text', 'help_text_long', 'hr_type',
                  'allowed_model', 'visibility', 'hr_visibility', 'state', 'choices', 'unique_name')
        read_only_fields = ('hr_type', 'hr_visibility')
        list_serializer_class = MultiUpdateNoDeleteListSerializer
