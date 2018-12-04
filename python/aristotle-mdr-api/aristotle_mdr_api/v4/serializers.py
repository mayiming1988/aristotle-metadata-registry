from typing import Iterable, Dict
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


class MultiUpdateListSerializer(serializers.ListSerializer):
    """
    To be used for multple updates on a list serializer
    Creates new models and deltes missing models
    Needs a non required IntegerField for id
    """

    perform_create = True
    perform_delete = True

    def update(self, instance: QuerySet, validated_data: Iterable[Dict]):
        db_mapping = {obj.id: obj for obj in instance}

        existing_data = []
        new_data = []
        for item in validated_data:
            if 'id' in item:
                existing_data.append(item)
            else:
                new_data.append(item)

        submitted_ids = [obj['id'] for obj in existing_data]
        return_list = []

        # Update existing item
        for item in existing_data:
            db_item = db_mapping.get(item['id'], None)
            # Make sure the id is a real item
            if db_item is not None:
                return_list.append(self.child.update(db_item, item))

        # Create new items
        if self.perform_create:
            for item in new_data:
                return_list.append(self.child.create(item))

        # Delete existing items
        if self.perform_delete:
            for iid, item in db_mapping.items():
                if iid not in submitted_ids:
                    # Item has been removed
                    item.delete()

        return return_list
