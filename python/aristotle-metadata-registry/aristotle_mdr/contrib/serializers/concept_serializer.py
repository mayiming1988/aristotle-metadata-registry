"""
Serializer
"""
from rest_framework import serializers
from django.core.serializers.base import Serializer

import json

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

        self.data = json.dumps(concept_serializer.data)

    def getvalue(self):
        return self.data



class BaseConceptSerializer(serializers.ModelSerializer):
    """ An 'abstract' concept serializer that has its attributes dynamically set """


def model_serializer_factory():
    """ Generalized serializer factory to dynamically set form fields """
    pass


