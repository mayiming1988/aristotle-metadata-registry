from rest_framework import serializers
from aristotle_mdr.contrib.issues.models import Issue
from aristotle_mdr.perms import user_can_view
from aristotle_mdr.models import _concept


class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ('name', 'description', 'item', 'isopen')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['submitter'] = user
        return super().create(validated_data)

    def validate_item(self, value):
        if not user_can_view(self.context['request'].user, value):
            raise serializers.ValidationError(
                'You don\'t have permission to create an issue against this item'
            )
        return value
