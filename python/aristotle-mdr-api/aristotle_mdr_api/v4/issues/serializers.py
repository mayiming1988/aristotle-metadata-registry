from django.urls import reverse
from rest_framework import serializers
from aristotle_mdr.contrib.issues.models import Issue, IssueComment, IssueLabel
from aristotle_mdr.perms import user_can_view


class IssueSerializer(serializers.ModelSerializer):

    labels = serializers.PrimaryKeyRelatedField(
        queryset=IssueLabel.objects.all(),
        many=True
    )

    class Meta:
        model = Issue
        fields = ('name', 'description', 'item', 'isopen', 'submitter', 'proposal_field', 'proposal_value', 'labels')

    submitter = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_item(self, value):
        if not user_can_view(self.context['request'].user, value):
            raise serializers.ValidationError(
                'You don\'t have permission to create an issue against this item'
            )
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['url'] = reverse('aristotle_issues:issue', args=[instance.item_id, instance.id])
        return rep


class IssueCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = IssueComment
        fields = ('body', 'author', 'issue', 'created')
        read_only_fields = ('created',)

    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def validate_issue(self, value):
        if not user_can_view(self.context['request'].user, value):
            raise serializers.ValidationError(
                'You don\'t have permission to comment on this issue'
            )
        return value

    def create(self, validated_data):
        return super().create(validated_data)
