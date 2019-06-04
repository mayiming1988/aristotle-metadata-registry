"""
Serializer
"""
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

import aristotle_mdr.models as MDR


class ConceptSerializer(serializers.ModelSerializer):
    pass


class Serializer(serializers.ModelSerializer):
    """This is a django serializer """
    class Meta:
        model = MDR.concept
        exclude = []

    def serialize(self, queryset, *args, **kwargs):
        # Override serialize method so that Django thinks this is a
        # Django serializer
        pass

