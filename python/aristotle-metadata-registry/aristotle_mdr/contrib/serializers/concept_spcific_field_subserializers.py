from aristotle_mdr.contrib.serializers.utils import SubSerializer
from aristotle_mdr.models import (
    SupplementaryValue,
    PermissibleValue,
    ValueMeaning,
    DedInputsThrough,
    DedDerivesThrough,
)
from aristotle_mdr.contrib.links.models import RelationRole


class PermissibleValueSerializer(SubSerializer):

    class Meta:
        model = PermissibleValue
        fields = ['value', 'meaning', 'order', 'start_date', 'end_date', 'uuid']


class SupplementaryValueSerializer(SubSerializer):

    class Meta:
        model = SupplementaryValue
        fields = ['value', 'meaning', 'order', 'start_date', 'end_date', 'uuid']


class ValueMeaningSerializer(SubSerializer):

    class Meta:
        model = ValueMeaning
        exclude = ('conceptual_domain',)


class DedInputsThroughSerializer(SubSerializer):

    class Meta:
        model = DedInputsThrough
        exclude = ('data_element_derivation',)


class DedDerivesThroughSerializer(SubSerializer):

    class Meta:
        model = DedDerivesThrough
        exclude = ('data_element_derivation',)


class RelationRoleSerializer(SubSerializer):

    class Meta:
        model = RelationRole
        exclude = ('relation',)
