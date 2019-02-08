from rest_framework import serializers
from aristotle_mdr.contrib.validators import models
from aristotle_mdr.contrib.validators.schema.load import load_schema

import json
import yaml
import jsonschema


class ValidateRulesSerializer(serializers.ModelSerializer):

    def validate_rules(self, value):
        # Make sure its valid yaml
        try:
            rules = yaml.safe_load(value)
        except yaml.YAMLError as ye:
            raise serializers.ValidationError(ye)

        # Make sure it conforms to the schema
        schema = json.loads(load_schema())
        try:
            jsonschema.validate(rules, schema)
        except jsonschema.exceptions.ValidationError as ve:
            raise serializers.ValidationError(ve)

        return value


class RegistryRuleSerializer(ValidateRulesSerializer):

    class Meta:
        model = models.RegistryValidationRules
        fields = ('id', 'rules')
        read_only_fields = ('id',)


class RARuleSerializer(ValidateRulesSerializer):

    class Meta:
        model = models.RAValidationRules
        fields = ('id', 'registration_authority', 'rules')
        read_only_fields = ('id',)

    def validate_registration_authority(self, value):
        if self.context['request'].user not in value.managers.all():
            raise serializers.ValidationError(
                'You don\'t have permission to create a rule on this registration authority'
            )
        return value
