from rest_framework import serializers
from aristotle_mdr.contrib.validators import models


class RegistryRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RegistryValidationRules
        fields = ('rules',)


class RARuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RAValidationRules
        fields = ('registration_authority', 'rules')

    def validate_registration_authority(self, value):
        if self.context['request'].user not in value.managers.all():
            raise serializers.ValidationError(
                'You don\'t have permission to create a rule on this registration authority'
            )
