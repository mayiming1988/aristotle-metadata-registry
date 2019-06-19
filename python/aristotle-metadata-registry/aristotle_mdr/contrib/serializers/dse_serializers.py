from rest_framework import serializers
from aristotle_dse.models import DSSClusterInclusion, DSSDEInclusion, DSSGrouping

excluded_fields = ('dss',)


class DSSClusterInclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSSClusterInclusion
        exclude = excluded_fields


class DSSDEInclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSSDEInclusion
        exclude = excluded_fields


class DSSGroupingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSSGrouping
        exclude = excluded_fields
