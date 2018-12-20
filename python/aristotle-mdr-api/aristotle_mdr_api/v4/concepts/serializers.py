from rest_framework import serializers
from aristotle_mdr.models import _concept


class ConceptSerializer(serializers.ModelSerializer):

    class Meta:
        model=_concept
        fields=('id', 'uuid', 'name', 'definition', 'short_definition')
