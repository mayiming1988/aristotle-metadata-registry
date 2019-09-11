
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError


class UniqueFieldsMixin(serializers.ModelSerializer):
    """
    Moves `UniqueValidator`'s from the validation stage to the save stage.
    It solves the problem with nested validation for unique fields on update.

    """
    _unique_fields = []

    def get_fields(self):
        self._unique_fields = []

        fields = super(UniqueFieldsMixin, self).get_fields()
        for field_name, field in fields.items():
            is_unique = any([isinstance(validator, UniqueValidator)
                             for validator in field.validators])
            if is_unique:
                self._unique_fields.append(field_name)
                field.validators = [
                    validator for validator in field.validators
                    if not isinstance(validator, UniqueValidator)]

        return fields

    def _validate_unique_fields(self, validated_data):
        for field_name in self._unique_fields:
            unique_validator = UniqueValidator(self.Meta.model.objects.all())
            unique_validator.set_context(self.fields[field_name])

            try:
                unique_validator(validated_data[field_name])
            except ValidationError as exc:
                raise ValidationError({field_name: exc.detail})

    def create(self, validated_data):
        self._validate_unique_fields(validated_data)
        return super(UniqueFieldsMixin, self).create(validated_data)

    def update(self, instance, validated_data):
        self._validate_unique_fields(validated_data)
        return super(UniqueFieldsMixin, self).update(instance, validated_data)
