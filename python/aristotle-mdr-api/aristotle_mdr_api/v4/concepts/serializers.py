from rest_framework import serializers
from aristotle_mdr.models import _concept, SupersedeRelationship
from django.urls import reverse
import reversion.models


class ConceptSerializer(serializers.ModelSerializer):

    absolute_url = serializers.SerializerMethodField('get_the_absolute_url')
    expand_node_get_url = serializers.SerializerMethodField('expand_this_node_get_url')

    def get_the_absolute_url(self, concept):
        return concept.get_absolute_url()

    def expand_this_node_get_url(self, concept):
        return reverse('api_v4:item:item_general_graphical', kwargs={'pk': concept.pk})

    class Meta:
        model = _concept
        fields = ('id', 'uuid', 'name', 'version', 'definition', 'short_definition',
                  'absolute_url', 'expand_node_get_url')


class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = reversion.models.Version
        fields = ('id', 'object_id', 'serialized_data', 'field_dict')


class SupersedeRelationshipSerialiser(serializers.ModelSerializer):

    absolute_url = serializers.SerializerMethodField('get_the_absolute_url')

    def get_the_absolute_url(self, relationship):
        return relationship.registration_authority.get_absolute_url()

    registration_authority = serializers.StringRelatedField()

    class Meta:
        model = SupersedeRelationship
        fields = ('older_item', 'newer_item', 'registration_authority', 'absolute_url')
