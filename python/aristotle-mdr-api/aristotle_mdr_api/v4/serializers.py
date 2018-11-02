from rest_framework import serializers
from aristotle_mdr.contrib.issues.models import Issue


class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ('name', 'description', 'item', 'isopen')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['submitter'] = user
        return super().create(validated_data)
