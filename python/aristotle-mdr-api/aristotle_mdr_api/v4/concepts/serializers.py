from rest_framework import serializers
from aristotle_mdr.models import _concept, SupersedeRelationship


class ConceptSerializer(serializers.ModelSerializer):

    absolute_url = serializers.SerializerMethodField('get_the_absolute_url')

    def get_the_absolute_url(self, concept):
        return concept.get_absolute_url()

    class Meta:
        model=_concept
        fields=('id', 'uuid', 'name', 'version', 'definition', 'short_definition', 'absolute_url')


class SupersedeRelationshipSerialiser(serializers.ModelSerializer):

    registration_authority = serializers.StringRelatedField()

    class Meta:
        model=SupersedeRelationship

        fields = ('older_item', 'newer_item', 'registration_authority')
