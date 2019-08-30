from django.conf import settings


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
