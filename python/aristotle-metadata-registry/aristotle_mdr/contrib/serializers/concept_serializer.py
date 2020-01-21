"""
Serializer for concept and all attached subfields
"""
from rest_framework import serializers

from django.core.serializers.base import Serializer as BaseDjangoSerializer
from django.core.serializers.base import DeserializedObject, build_instance
from django.apps import apps
from django.db import DEFAULT_DB_ALIAS
from django.conf import settings

from aristotle_mdr.contrib.custom_fields.models import CustomValue
from aristotle_mdr.contrib.slots.models import Slot
from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier
from aristotle_mdr.models import (
    RecordRelation,
    SupplementaryValue,
    PermissibleValue,
    ValueMeaning,
    DedInputsThrough,
    DedDerivesThrough,
    aristotleComponent
)
from aristotle_mdr.contrib.serializers.utils import get_concept_field_names, get_relation_field_names
from aristotle_mdr.contrib.links.models import RelationRole
from aristotle_mdr.utils.utils import cloud_enabled

import json as JSON

import logging
logger = logging.getLogger(__name__)


class SubSerializer(serializers.ModelSerializer):
    """Base class for subserializers"""
    id = serializers.SerializerMethodField()

    def get_id(self, item):
        """Get pk here in case we are not using the auto id field"""
        return item.pk


class IdentifierSerializer(SubSerializer):

    class Meta:
        model = ScopedIdentifier
        fields = ['namespace', 'identifier', 'version', 'order', 'id']


class CustomValuesSerializer(SubSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = CustomValue
        fields = ['field', 'name', 'content', 'id']

    def get_name(self, custom_value):
        return custom_value.field.name


class SlotsSerializer(SubSerializer):
    class Meta:
        model = Slot
        fields = ['name', 'value', 'order', 'permission', 'id']


class OrganisationRecordsSerializer(SubSerializer):
    class Meta:
        model = RecordRelation
        fields = ['organization_record', 'type', 'id']


class SupplementaryValueSerializer(SubSerializer):

    class Meta:
        model = SupplementaryValue
        fields = ['value', 'meaning', 'order', 'start_date', 'end_date', 'id']


class PermissibleValueSerializer(SubSerializer):

    class Meta:
        model = PermissibleValue
        fields = ['value', 'meaning', 'order', 'start_date', 'end_date', 'id']


class ValueMeaningSerializer(SubSerializer):

    class Meta:
        model = ValueMeaning
        exclude = ('conceptual_domain',)


class DedDerivesThroughSerializer(SubSerializer):

    class Meta:
        model = DedDerivesThrough
        exclude = ('data_element_derivation',)


class DedInputsThroughSerializer(SubSerializer):

    class Meta:
        model = DedInputsThrough
        exclude = ('data_element_derivation',)


class RelationRoleSerializer(SubSerializer):

    class Meta:
        model = RelationRole
        exclude = ('relation',)


class BaseSerializer(serializers.ModelSerializer):
    slots = SlotsSerializer(many=True)
    customvalue_set = CustomValuesSerializer(many=True)

    identifiers = IdentifierSerializer(many=True)
    org_records = OrganisationRecordsSerializer(many=True)

    stewardship_organisation = serializers.PrimaryKeyRelatedField(
        pk_field=serializers.UUIDField(format='hex'),
        read_only=True)

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

        if 'aristotle_dse' in settings.INSTALLED_APPS:
            # Add extra serializers if DSE is installed
            from aristotle_mdr.contrib.serializers.dse_serializers import (
                DSSGroupingSerializer,
                DSSClusterInclusionSerializer,
                DSSDEInclusionSerializer,
                DistributionDataElementPathSerializer,
            )

            self.field_subserializer_mapping.update({
                'dssdeinclusion_set': DSSDEInclusionSerializer(many=True),
                'dssclusterinclusion_set': DSSClusterInclusionSerializer(many=True),
                'groups': DSSGroupingSerializer(many=True),
                'distributiondataelementpath_set': DistributionDataElementPathSerializer(many=True),
            })

        if 'comet' in settings.INSTALLED_APPS:
            from aristotle_mdr.contrib.serializers.indicator_serializers import (
                IndicatorNumeratorSerializer,
                IndicatorDenominatorSerializer,
                IndicatorDisaggregationSerializer,
                IndicatorInclusionSerializer
            )

            self.field_subserializer_mapping.update({
                'indicatornumeratordefinition_set': IndicatorNumeratorSerializer(many=True),
                'indicatordenominatordefinition_set': IndicatorDenominatorSerializer(many=True),
                'indicatordisaggregationdefinition_set': IndicatorDisaggregationSerializer(many=True),
                'indicatorinclusion_set': IndicatorInclusionSerializer(many=True)
            })
        if cloud_enabled():
            from aristotle_cloud.contrib.serializers.serializers import ReferenceLinkSerializer
            self.field_subserializer_mapping.update({
                'metadatareferencelink_set': ReferenceLinkSerializer(many=True)
            })
        self.whitelisted_fields = [
            'statistical_unit',
            'dssgrouping_set',
        ] + list(self.field_subserializer_mapping.keys())

    def _get_class_for_serializer(self, concept):
        return concept.__class__

    def generate_serializer(self, concept):
        """ Generate the serializer class """
        concept_class = self._get_class_for_serializer(concept)
        Serializer = self._generate_serializer_class(concept_class)

        return Serializer

    def _generate_serializer_class(self, concept_class):
        universal_fields = ('slots', 'customvalue_set', 'org_records', 'identifiers', 'stewardship_organisation',
                            'workgroup', 'submitter')

        concept_fields = get_concept_field_names(concept_class)
        relation_fields = get_relation_field_names(concept_class, whitelisted_fields=self.whitelisted_fields)

        included_fields = concept_fields + relation_fields + universal_fields

        # Generate metaclass dynamically
        meta_attrs = {'model': concept_class,
                      'fields': included_fields}
        Meta = type('Meta', tuple(), meta_attrs)

        serializer_attrs = {}
        for field_name in relation_fields:
            if field_name in self.field_subserializer_mapping:
                # Field is for something that should have it's component fields serialized
                serializer = self.field_subserializer_mapping[field_name]
                serializer_attrs[field_name] = serializer

        serializer_attrs['Meta'] = Meta

        # Generate serializer dynamically
        Serializer = type('Serializer', (BaseSerializer,), serializer_attrs)
        return Serializer

    def _get_class_for_deserializer(self, json):
        data = JSON.loads(json)
        return apps.get_model(data['serialized_model'])

    def generate_deserializer(self, json):
        """ Generate the deserializer """
        concept_model = self._get_class_for_deserializer(json)

        Deserializer = self._generate_serializer_class(concept_model)
        return Deserializer


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
