from typing import Iterable, Dict
from django.db.models import Model
from django.db.models.query import QuerySet
from rest_framework import serializers


class MultiUpdateListSerializer(serializers.ListSerializer):
    """
    To be used for multple updates on a list serializer
    Creates new models and deltes missing models
    Needs a non required IntegerField for id
    """

    perform_create = True
    perform_delete = True

    def update(self, instance: QuerySet, validated_data: Iterable[Dict]):
        db_mapping: Dict[int, Model] = {obj.id: obj for obj in instance}

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
            for iid, inst in db_mapping.items():
                if iid not in submitted_ids:
                    # Item has been removed
                    inst.delete()

        return return_list


class MultiUpdateNoDeleteListSerializer(MultiUpdateListSerializer):
    perform_delete = False
