"""
Serializer
"""
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from django.core.serializers.base import Serializer, DeserializedObject, build_instance

import io

import logging
logger = logging.getLogger(__name__)


def Deserializer(json, **options):
    """ Deserialize JSON back into Django ORM instances.
        Django deserializers yield a DeserializedObject generator.
        DeserializedObjects are thin wrappers over POPOs. """

    # Parse a stream into Python's native datatype
    stream = io.BytesIO(json)
    data = JSONParser().parse(stream)


    # Restore those datatypes into a dictionary of validated data
    serializer = Serializer(data=data)
    serializer.is_valid()

    # concept =  build_instance()'

class CustomValueSerializer(serializers.ModelSerializer):
    pass


class BaseSerializer(serializers.ModelSerializer):
    """ An 'abstract' concept serializer that has its attributes dynamically set.
        Used for simple concepts that may have different fields, but not aristotleComponents """
    class Meta:
        fields = tuple()
        abstract = True


class ModelSerializerFactory():
    """ Generalized serializer factory to dynamically set form fields for simpler concepts """

    def _get_nonrelation_fields(self, concept):
        """Internal helper function to get fields that are actually **on** the model.
           Returns a tuple of fields"""
        return tuple([field.name for field in concept._meta.get_fields() if not field.is_relation])

    def _get_relation_fields(self, concept):
        """ Internal helper function to get related fields
            Returns a tuple of fields"""
        related_fields = []

        for field in concept._meta.get_fields():
            if field.is_relation:
                if hasattr(field, 'get_accessor_name'):
                    related_fields.append(field.get_accessor_name())
                else:
                    related_fields.append(field.name)
        return tuple(related_fields)

    def _whitelist_fields(self, fields):
        pass

    def _get_model(self, concept):
        return concept.__class__

    def generate_serializer(self, concept):

        concept_model = self._get_model(concept)
        concept_fields = self._get_nonrelation_fields(concept)

        class Serializer(BaseSerializer):
            class Meta:
                model = concept_model
                fields = concept_fields

        return Serializer


class Serializer(Serializer):
    """This is a django serializer that has a 'composed' DRF Framework inside. """

    data = {}
    def serialize(self, queryset, stream=None, fields=None, use_natural_foreign_keys=False,
                  use_natural_primary_keys=False, progress_output=None, **options):

        concept = queryset[0]

        # Generate the serializer
        ModelSerializer = ModelSerializerFactory().generate_serializer(concept)
        # Instanciate the serializer
        serializer = ModelSerializer(concept)

        self.data = JSONRenderer().render(serializer.data)

    def getvalue(self):
        # Get value must be overridden because django-reversion calls *getvalue* rather than serialize directly
        return self.data



