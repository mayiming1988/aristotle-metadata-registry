"""
Serializer for concept and all attached subfields
"""
from rest_framework import serializers

from django.core.serializers.base import Serializer as BaseDjangoSerializer
from django.core.serializers.base import DeserializedObject, build_instance
from django.apps import apps
from django.db import DEFAULT_DB_ALIAS


from aristotle_mdr.models import (
    ValueDomain,
    DataElementConcept,
    aristotleComponent
)
from aristotle_mdr.contrib.serializers.utils import (
    get_comet_field_serializer_mapping,
    get_dse_field_serializer_mapping,
    get_aristotle_ontology_serializer_mapping,
)
from aristotle_mdr.contrib.serializers.concept_general_field_subserializers import (
    IdentifierSerializer,
    SlotsSerializer,
    CustomValuesSerializer,
    OrganisationRecordsSerializer,
)

from aristotle_mdr.contrib.serializers.concept_spcific_field_subserializers import (
    PermissibleValueSerializer,
    SupplementaryValueSerializer,
    ValueMeaningSerializer,
    DedInputsThroughSerializer,
    DedDerivesThroughSerializer,
    RelationRoleSerializer,
)

import json as JSON

import logging

logger = logging.getLogger(__name__)


class ConceptBaseSerializer(serializers.ModelSerializer):
    """
    This Class is the serializer representation of the _concept model.
    It includes the universal fields for every _concept instance.
    """
    slots = SlotsSerializer(many=True)
    customvalue_set = CustomValuesSerializer(many=True)
    identifiers = IdentifierSerializer(many=True)
    org_records = OrganisationRecordsSerializer(many=True)
    stewardship_organisation = serializers.PrimaryKeyRelatedField(
        pk_field=serializers.UUIDField(format='hex'),
        read_only=True
    )

# To begin serializing an added subitem:
#   1. Add a ModelSerializer for your subitem
#   2. Add to FIELD_SUBSERIALIZER_MAPPING


class ConceptSerializerFactory:
    """ Generalized serializer factory to dynamically set form fields for simpler concepts """
    field_subserializer_mapping = {
        'permissiblevalue_set': PermissibleValueSerializer(many=True),
        'supplementaryvalue_set': SupplementaryValueSerializer(many=True),
        'valuemeaning_set': ValueMeaningSerializer(many=True),
        'dedinputsthrough_set': DedInputsThroughSerializer(many=True),
        'dedderivesthrough_set': DedDerivesThroughSerializer(many=True),
        'relationrole_set': RelationRoleSerializer(many=True),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.field_subserializer_mapping.update({
            **get_comet_field_serializer_mapping(),
            **get_dse_field_serializer_mapping(),
            **get_aristotle_ontology_serializer_mapping(),
        })

        self.whitelisted_fields = [
            'statistical_unit',
            'dssgrouping_set',
        ] + list(self.field_subserializer_mapping.keys())

    def get_field_name(self, field):
        if hasattr(field, 'get_accessor_name'):
            return field.get_accessor_name()
        else:
            return field.name

    def _get_concept_fields(self, model_class):
        """
        Internal helper function to get fields that are actually **on** the model.
        This function excludes Foreign Key fields (relation fields).
        :param model_class: Model to get the fields from.
        :return: Tuple of fields
        """
        fields = []
        for field in model_class._meta.get_fields():
            if not field.is_relation or field.many_to_one:  # Exclude data field or foreign key field
                if not field.name.startswith('_'):  # Don't serialize internal fields
                    fields.append(field.name)

        return tuple(fields)

    def _get_concept_relation_fields(self, model_class):
        """
        Internal helper function to get related (Foreign key) fields.
        :param model_class: Model to get the fields from.
        :return: Tuple of fields
        """
        related_fields = []

        for field in model_class._meta.get_fields():
            if not field.name.startswith('_'):
                # Don't serialize internal fields
                if field.is_relation:
                    # Check if the model class is the parent of the item, we don't want to serialize up the chain
                    field_model = field.related_model
                    if issubclass(field_model, aristotleComponent):
                        # If it's a subclass of aristotleComponent it should have a parent
                        parent_model = field_model.get_parent_model()
                        if not parent_model:
                            # This aristotle component has no parent model
                            related_fields.append(self.get_field_name(field))
                        else:
                            if field_model.get_parent_model() == model_class:
                                # If the parent is the model we're serializing, right now
                                related_fields.append(self.get_field_name(field))
                            else:
                                # It's the child, we don't want to serialize
                                pass
                    else:
                        # Just a normal field
                        related_fields.append(self.get_field_name(field))

        return tuple([field for field in related_fields if field in self.whitelisted_fields])

    def generate_serializer(self, concept):
        """ Generate the serializer class """
        concept_class = self._get_class_for_serializer(concept)
        Serializer = self._generate_serializer_class(concept_class)

        return Serializer

    def generate_deserializer(self, json):
        """ Generate the deserializer """
        concept_model = self._get_class_for_deserializer(json)

        Deserializer = self._generate_serializer_class(concept_model)
        return Deserializer

    def _get_class_for_serializer(self, concept):
        return concept.__class__

    def _generate_serializer_class(self, concept_class):
        universal_fields = ('slots', 'customvalue_set', 'org_records', 'identifiers', 'stewardship_organisation',
                            'workgroup', 'submitter')

        concept_fields = self._get_concept_fields(concept_class)
        concept_relation_fields = self._get_concept_relation_fields(concept_class)

        included_fields = concept_fields + concept_relation_fields + universal_fields

        # Generate metaclass dynamically
        meta_attrs = {'model': concept_class,
                      'fields': included_fields}
        Meta = type('Meta', tuple(), meta_attrs)

        serializer_attrs = {}
        for field_name in concept_relation_fields:
            if field_name in self.field_subserializer_mapping:
                # Field is for something that should have it's component fields serialized
                serializer = self.field_subserializer_mapping[field_name]
                serializer_attrs[field_name] = serializer

        serializer_attrs['Meta'] = Meta

        # Generate serializer class dynamically
        Serializer = type('Serializer', (ConceptBaseSerializer,), serializer_attrs)
        return Serializer

    def _get_class_for_deserializer(self, json):
        data = JSON.loads(json)
        return apps.get_model(data['serialized_model'])


class Serializer(BaseDjangoSerializer):
    """This is a django serializer that has a 'composed' DRF Serializer inside. """
    data: dict = {}

    def serialize(self, queryset, stream=None, fields=None, use_natural_foreign_keys=False,
                  use_natural_primary_keys=False, progress_output=None, **options):
        concept = queryset[0]

        # Generate the serializer
        ModelSerializer = ConceptSerializerFactory().generate_serializer(concept)

        # Instantiate the serializer
        serializer = ModelSerializer(concept)

        # Add the app label as a key to the json so that the deserializer can be generated
        data = serializer.data
        data['serialized_model'] = concept._meta.label_lower

        self.data = JSON.dumps(data)

    def getvalue(self):
        # Get value must be overridden because django-reversion calls *getvalue* rather than serialize directly
        return self.data


def Deserializer(json, using=DEFAULT_DB_ALIAS, **options):
    # TODO: fix
    """ Deserialize JSON back into Django ORM instances.
        Django deserializers yield a DeserializedObject generator.
        DeserializedObjects are thin wrappers over POPOs. """
    m2m_data = {}

    # Generate the serializer
    ModelDeserializer = ConceptSerializerFactory().generate_deserializer(json)

    # Instantiate the serializer
    data = JSON.loads(json)

    Model = apps.get_model(data['serialized_model'])

    # Deserialize the data
    serializer = ModelDeserializer(data=data)

    serializer.is_valid(raise_exception=True)

    obj = build_instance(Model, data, using)

    yield DeserializedObject(obj, m2m_data)
