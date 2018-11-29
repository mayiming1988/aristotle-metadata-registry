from rest_framework import serializers

from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomField
        fields = ('name', 'type', 'help_text', 'hr_type')
        read_only_fields = ('hr_type',)
