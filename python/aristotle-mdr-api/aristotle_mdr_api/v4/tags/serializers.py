from aristotle_mdr.contrib.favourites.models import Tag, Favourite
from rest_framework import serializers
from aristotle_mdr_api.v4.fields import CurrentProfileDefault


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'description', 'created', 'profile')
        read_only_fields = ('id', 'created', 'profile')

    profile = serializers.HiddenField(
        default=CurrentProfileDefault()
    )


class ItemTagSerializer(serializers.Serializer):

    tags = TagSerializer(many=True, validators=[])

    def update(self, instance, validated_data):
        user_profile = self.context['request'].user.profile
        favs = instance.select_related('tag').all()

        tags_map = {f.tag.name: f.tag for f in favs}

        tags = set([tag['name'] for tag in validated_data['tags']])
        current_set = set(tags_map.keys())
        new = tags - current_set
        deleted = current_set - tags

        for tag in new:
            tag_obj, created = Tag.objects.get_or_create(
                profile=user_profile,
                name=tag,
                primary=False
            )
            Favourite.objects.create(
                tag=tag_obj,
                item=self.context['item']
            )
            tags_map[tag_obj.name] = tag_obj

        for tag in deleted:
            tag_obj, created = Tag.objects.get_or_create(
                profile=user_profile,
                name=tag,
                primary=False
            )
            Favourite.objects.filter(
                tag=tag_obj,
                item=self.context['item']
            ).delete()
            del tags_map[tag]

        tag_serializer = TagSerializer(tags_map.values(), many=True)

        return {
            'tags': tag_serializer.data
        }
