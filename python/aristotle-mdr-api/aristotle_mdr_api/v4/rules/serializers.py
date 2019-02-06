from rest_framework import serializers
from aristotle_mdr.contrib.validators import models
from aristotle_mdr.contrib.validators.schema.load import load_schema

import yaml
import jsonschema


class ValidateRulesSerializer(serializers.ModelSerializer):

    def validate_rules(self, value):
        schema = load_schema()

        try:
            rules = yaml.safe_load(value)
        except yaml.YAMLError as ye:
            raise serializers.ValidationError(ye)

        try:
            jsonschema.validate(rules, schema)
        except jsonschema.exceptions.ValidationError as ve:
            raise serializers.ValidationError(ve)


class RegistryRuleSerializer(ValidateRulesSerializer):

    class Meta:
        model = models.RegistryValidationRules
        fields = ('rules',)


class RARuleSerializer(ValidateRulesSerializer):

    class Meta:
        model = models.RAValidationRules
        fields = ('registration_authority', 'rules')

    def validate_registration_authority(self, value):
        if self.context['request'].user not in value.managers.all():
            raise serializers.ValidationError(
                'You don\'t have permission to create a rule on this registration authority'
            )
