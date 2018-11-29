from django.urls import reverse
from django.db.models.query import QuerySet
from rest_framework import serializers
from aristotle_mdr.contrib.issues.models import Issue, IssueComment
from aristotle_mdr.perms import user_can_view
from aristotle_mdr.models import _concept


class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ('name', 'description', 'item', 'isopen', 'submitter')

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


class MultiUpdateListMixin:
    """
    To be used for multple updates on a list serializer
    Creates new models and deltes missing models
    """

    def update(self, instance: QuerySet, validated_data: dict):
        db_mapping = {obj.id: obj for obj in instance}
        data_mapping = {obj['id']: obj for obj in validated_data}

        return_list = []
        for iid, data in data_mapping.items():
            db_item = db_mapping.get(iid, None)
            if db_item is None:
                # Submitted new item
                return_list.append(self.child.create(data))
            else:
                # Submitted existing item
                return_list.append(self.child.update(data))

        for iid, item in db_mapping.items():
            if iid not in data_mapping:
                # Item has been removed
                item.delete()

        return return_list
