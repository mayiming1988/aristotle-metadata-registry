from rest_framework import serializers
from aristotle_mdr.models import _concept, SupersedeRelationship


class ConceptSerializer(serializers.ModelSerializer):

    class Meta:
        model=_concept
        fields=('id', 'uuid', 'name', 'definition', 'short_definition')


class SupersedeRelationshipSerialiser(serializers.ModelSerializer):

    registration_authority = serializers.StringRelatedField()

    class Meta:
        model=SupersedeRelationship

        fields = ('older_item', 'newer_item', 'registration_authority')
