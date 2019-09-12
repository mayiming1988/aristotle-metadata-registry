from django.conf import settings
from rest_framework import serializers
from django.utils.translation import ugettext as _
from django.utils.text import get_text_list


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
            'objectclassspecialisationnarrowerclass_set': ObjectClassSpecialisationNarrowerClassSerializer(many=True, required=False),
        }
    return mapping


def construct_change_message_for_validated_data(validated_data, model=None):
    """
    This function returns the string representation of the modified fields from an API serialized data.
    Particularly useful in update() functions of Serializers.
    :param validated_data: Dictionary containing field names as keys and changed values.
    :param model: Model from which the fields' verbose names will be retrieved.
    :return: String. Description of the modified fields of a serializer's validated data.
    """

    change_message = ""
    fields_verbose_names = []

    for field_name in validated_data.keys():
        field = model._meta.get_field(field_name)
        if field.is_relation:
            fields_verbose_names.append(field.related_model._meta.verbose_name.lower())
        else:
            fields_verbose_names.append(field.verbose_name)

    if fields_verbose_names:
        change_message = _('Changed %s.') % get_text_list(fields_verbose_names, _('and'))

    return change_message
