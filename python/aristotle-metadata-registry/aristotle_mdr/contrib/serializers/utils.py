from django.conf import settings
from rest_framework import serializers


class SubSerializer(serializers.ModelSerializer):
    """Base class for subserializers"""
    id = serializers.SerializerMethodField()

    def get_id(self, item):
        """Get pk here in case we are not using the auto id field"""
        return item.pk


def get_comet_field_serializer_mapping():
    mapping = {}
    if 'comet' in settings.INSTALLED_APPS:
        from aristotle_mdr.contrib.serializers.comet_indicator_serializers import (
            IndicatorNumeratorSerializer,
            IndicatorDenominatorSerializer,
            IndicatorDisaggregationSerializer,
            IndicatorInclusionSerializer,
        )

        mapping = {
            'indicatornumeratordefinition_set': IndicatorNumeratorSerializer(many=True),
            'indicatordenominatordefinition_set': IndicatorDenominatorSerializer(many=True),
            'indicatordisaggregationdefinition_set': IndicatorDisaggregationSerializer(many=True),
            'indicatorinclusion_set': IndicatorInclusionSerializer(many=True)
        }
    return mapping


def get_dse_field_serializer_mapping():
    mapping = {}
    if 'aristotle_dse' in settings.INSTALLED_APPS:
        # Add extra serializers if DSE is installed
        from aristotle_mdr.contrib.serializers.dse_serializers import (
            DSSGroupingSerializer,
            DSSClusterInclusionSerializer,
            DSSDEInclusionSerializer,
            DistributionDataElementPathSerializer,
        )

        mapping = {
            'dssdeinclusion_set': DSSDEInclusionSerializer(many=True),
            'dssclusterinclusion_set': DSSClusterInclusionSerializer(many=True),
            'groups': DSSGroupingSerializer(many=True),
            'distributiondataelementpath_set': DistributionDataElementPathSerializer(many=True),
        }
    return mapping


def get_aristotle_ontology_serializer_mapping():
    mapping = {}
    if 'aristotle_ontology' in settings.INSTALLED_APPS:
        from aristotle_mdr.contrib.serializers.aristotle_ontology_serializers import (
            ObjectClassSpecialisationNarrowerClassSerializer
        )

        mapping = {
            'objectclassspecialisationnarrowerclass_set': ObjectClassSpecialisationNarrowerClassSerializer(many=True),
        }
    return mapping
