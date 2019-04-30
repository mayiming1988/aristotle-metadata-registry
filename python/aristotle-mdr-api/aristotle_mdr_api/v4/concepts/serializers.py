from rest_framework import serializers
from django.urls import reverse

from reversion.models import Version

from aristotle_mdr.contrib.publishing.models import VersionPermissions
from aristotle_mdr.models import _concept, SupersedeRelationship
from aristotle_mdr_api.v4.serializers import VersionVisibilityPermissionSerializer

import logging
logger = logging.getLogger(__name__)

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
        model = Version
        fields = ('id', 'object_id', 'serialized_data')


class VersionPermissionsSerializer(serializers.ModelSerializer):
    version_id = serializers.IntegerField(required=False)

    class Meta:
        model = VersionPermissions
        fields = ('version_id','visibility')
        list_serializer_class = VersionVisibilityPermissionSerializer

    def validate_version_id(self, value):
        if value not in self.context.get('version_ids'):
            raise serializers.ValidationError()
        return value


class SupersedeRelationshipSerialiser(serializers.ModelSerializer):

    absolute_url = serializers.SerializerMethodField('get_the_absolute_url')

    def get_the_absolute_url(self, relationship):
        return relationship.registration_authority.get_absolute_url()

    registration_authority = serializers.StringRelatedField()

    class Meta:
        model = SupersedeRelationship
        fields = ('older_item', 'newer_item', 'registration_authority', 'absolute_url')
