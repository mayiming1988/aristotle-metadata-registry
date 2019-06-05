"""
Serializer
"""
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from django.core.serializers.base import Serializer, DeserializedObject, build_instance

import io

import aristotle_mdr.models as MDR

import logging
logger = logging.getLogger(__name__)


class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MDR._concept
        fields = ('id', 'uuid', 'name', 'version', 'definition', 'short_definition')



class Serializer(Serializer):
    """This is a django serializer that has a 'composed' DRF Framework inside. """

    data = None
    # To avoid an attribute error with django-reversion
    stream = None

    def serialize(self, queryset, stream=None, fields=None, use_natural_foreign_keys=False,
                  use_natural_primary_keys=False, progress_output=None, **options):

        concept = queryset[0]
        concept_serializer = ConceptSerializer(concept)

        self.data = JSONRenderer().render(concept_serializer.data)

    def getvalue(self):
        # Get value must be overridden because django-reversion calls *getvalue* rather than serialize directly
        return self.data


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

    # concept =  build_instance()


class BaseSerializer(serializers.ModelSerializer):
    """ An 'abstract' concept serializer that has its attributes dynamically set.
        Used for simple concepts that may have different fields, but not aristotleComponents """

    class Meta:
        model = None
        fields = tuple()


class ModelSerializerFactory():
    """ Generalized serializer factory to dynamically set form fields for simpler concepts """

    def _get_extra_fields(attrs):
        """Internal helper function to get the extra fields.
           Returns a dictionary"""
        pass

    def generate_serializer(self):
        """ Function that actually generates the serializer """
        pass


