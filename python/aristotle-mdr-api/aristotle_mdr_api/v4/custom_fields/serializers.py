from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from aristotle_mdr_api.v4.serializers import MultiUpdateNoDeleteListSerializer
from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    order = serializers.IntegerField()
    name = serializers.CharField(max_length=1000)
    choices = serializers.CharField(allow_blank=True, default='')
    system_name = serializers.CharField(validators=[])

    already_found_duplicates = False

    def to_representation(self, instance) -> str:
        representation = super().to_representation(instance)
        try:
            representation['system_name'] = self.get_cleaned_system_name(representation['system_name'])
        except KeyError:
            representation['system_name'] = ''

        return representation

    def validate(self, data):
        system_name = self.get_namespaced_system_name(data)

        if 'id' not in data:
            # It's a newly created instance, check that the newly created instance is not already in database
            if CustomField.objects.filter(system_name=system_name).count() > 0:
                raise serializers.ValidationError(
                    'System name {} is not unique. Please choose another.'.format(data['system_name'])
                )
        if not self.already_found_duplicates:
            system_names = [self.get_namespaced_system_name(initial_dict) for initial_dict in self.initial_data]
            if len(system_names) != len(set(system_names)):
                duplicates = [val for val in system_names if system_names.count(val) > 1]

                self.already_found_duplicates = True
                raise serializers.ValidationError("Duplicated system names {} found!".format(duplicates))

        return data

    def get_namespaced_system_name(self, validated_data) -> str:
        system_name = validated_data['system_name']

        if 'allowed_model' in validated_data:
            if validated_data['allowed_model'] is None:
                allowed_model = 'all'
            else:
                allowed_model = validated_data['allowed_model']
        else:
            allowed_model = 'all'

        if type(allowed_model) == int:
            allowed_model = ContentType.objects.get(pk=int(allowed_model)).model

        allowed_model = str(allowed_model).replace(' ', '')
        system_name = '{namespace}:{system_name}'.format(namespace=allowed_model,
                                                         system_name=system_name)

        return system_name

    def get_cleaned_system_name(self, system_name) -> str:
        return system_name.split(':', 1)[-1]  # Remove the namespacing for display in the edit view

    def create(self, validated_data) -> CustomField:
        validated_data['system_name'] = self.get_namespaced_system_name(validated_data)

        return CustomField.objects.create(**validated_data)

    def update(self, instance, validated_data ) -> CustomField:
        instance.order = validated_data.get('order', instance.order)
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.state = validated_data.get('state', instance.state)
        instance.help_text = validated_data.get('help_text', instance.help_text)
        instance.help_text_long = validated_data.get('help_text_long', instance.help_text_long)
        instance.choices = validated_data.get('choices', instance.choices)
        instance.system_name = self.get_namespaced_system_name(validated_data)

        instance.save()

        return instance

    class Meta:
        model = CustomField
        fields = ('id', 'order', 'name', 'type', 'system_name', 'help_text', 'help_text_long', 'hr_type',
                  'allowed_model', 'visibility', 'hr_visibility', 'state', 'choices')
        read_only_fields = ('hr_type', 'hr_visibility')

        list_serializer_class = MultiUpdateNoDeleteListSerializer
