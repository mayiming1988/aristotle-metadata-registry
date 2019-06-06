"""
Serializer
"""
from rest_framework import serializers

from django.core.serializers.base import Serializer, DeserializedObject, build_instance

from aristotle_mdr.contrib.custom_fields.models import CustomValue
from aristotle_mdr.contrib.slots.models import Slot
from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier
from aristotle_dse.models import DSSClusterInclusion, DSSDEInclusion, DSSGrouping
from aristotle_mdr.models import RecordRelation

import json

import logging

logger = logging.getLogger(__name__)


class IdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScopedIdentifier
        fields = ['namespace', 'identifier', 'version', 'order']


class CustomValuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomValue
        fields = ['field', 'content']


class SlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['name', 'length', 'value', 'order', 'permission']


class OrganisationRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordRelation
        fields = ['organization_record', 'type']


excluded_fields = ('inline_field_layout',
                   'inline_field_order'
                   'dss',)


class DSSClusterInclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSSClusterInclusion
        exclude = excluded_fields


class DSSDEInclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSSDEInclusion
        exclude = excluded_fields

class DSSGroupingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSSGrouping
        exclude = excluded_fields


class Serializer(serializers.ModelSerializer):
    slots = SlotsSerializer(many=True)
    customvalue_set = CustomValuesSerializer(many=True)
    identifiers = IdentifierSerializer(many=True)
    org_records = OrganisationRecordsSerializer(many=True)

    stewardship_organisation = serializers.PrimaryKeyRelatedField(
        pk_field=serializers.UUIDField(format='hex'),
        read_only=True)



class ConceptSerializerFactory():
    """ Generalized serializer factory to dynamically set form fields for simpler concepts """
    UNIVERSAL_FIELDS = ('slots', 'customvalue_set', 'identifiers', 'org_records')

    FIELD_SUBSERIALIZER_MAPPING = {'dssdeinclusion_set': DSSDEInclusionSerializer,
                                   'dssclusterinclusion_set': DSSClusterInclusionSerializer}

    def _get_concept_fields(self, concept):
        """Internal helper function to get fields that are actually **on** the model.
           Returns a tuple of fields"""
        fields = []
        for field in concept._meta.get_fields():
            if not field.is_relation:
                if not field.name.startswith('_'):
                    # Don't serialize internal fields
                    fields.append(field.name)

        return tuple(fields)

    def _get_relation_fields(self, concept):
        """ Internal helper function to get related fields
            Returns a tuple of fields"""

        whitelisted_fields = ['dssdeinclusion_set',
                              'dssclusterinclusion_set',
                              'parent_dss',
                              'indicatornumeratordefinition_set',
                              'indicatordenominatordefinition_set',
                              'indicatordisaggregationdefinition_set',
                              'statistical_unit',
                              'dssgrouping_set']
        related_fields = []
        for field in concept._meta.get_fields():
            if not field.name.startswith('_'):
                # Don't serialize internal fields
                if field.is_relation:
                    if hasattr(field, 'get_accessor_name'):
                        related_fields.append(field.get_accessor_name())
                    else:
                        related_fields.append(field.name)

        return tuple([field for field in related_fields if field in whitelisted_fields])

    def _get_model(self, concept):
        return concept.__class__


    def generate_serializer(self, concept):
        """ Generate the serializer class """
        universal_fields = ('slots', 'customvalue_set', 'org_records', 'identifiers', 'stewardship_organisation',
                            'workgroup', 'submitter')

        concept_model = self._get_model(concept)

        concept_fields = self._get_concept_fields(concept)

        relation_fields = self._get_relation_fields(concept)

        included_fields = concept_fields + relation_fields + universal_fields

        Serializer = None

        return Serializer

    def generate_deserializer(self, json):
        """ Generate the deserializer """
        pass


class Serializer(Serializer):
    """This is a django serializer that has a 'composed' DRF Framework inside. """
    data = {}

    def serialize(self, queryset, stream=None, fields=None, use_natural_foreign_keys=False,
                  use_natural_primary_keys=False, progress_output=None, **options):

        concept = queryset[0]

        if concept._meta.object_name == 'Data Set Specification':
            pass
        # Generate the serializer
        ModelSerializer = ConceptSerializerFactory().generate_serializer(concept)

        # Instantiate the serializer
        serializer = ModelSerializer(concept)

        # Add the app label as a key to the json so that the deserializer can be instantiated
        data = serializer.data
        data['model'] = '{}.{}'.format(concept._meta.app_label, concept._meta.object_name)

        raise ValueError(data)


        self.data = json.dumps(data)


    def getvalue(self):
        # Get value must be overridden because django-reversion calls *getvalue* rather than serialize directly
        return self.data

def Deserializer(json, **options):
    """ Deserialize JSON back into Django ORM instances.
        Django deserializers yield a DeserializedObject generator.
        DeserializedObjects are thin wrappers over POPOs. """
    raise NotImplementedError("Deserializer has not been implemented yet")
