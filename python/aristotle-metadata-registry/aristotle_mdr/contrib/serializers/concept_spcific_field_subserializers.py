from aristotle_mdr.contrib.serializers.utils import SubSerializer
from aristotle_mdr.models import (
    SupplementaryValue,
    PermissibleValue,
    ValueMeaning,
    DedInputsThrough,
    DedDerivesThrough,
)
from aristotle_mdr.contrib.links.models import RelationRole
from aristotle_ontology.models import ObjectClassSpecialisationNarrowerClass


class PermissibleValueSerializer(SubSerializer):

    class Meta:
        model = PermissibleValue
        fields = ['value', 'meaning', 'order', 'start_date', 'end_date', 'id']


class SupplementaryValueSerializer(SubSerializer):

    class Meta:
        model = SupplementaryValue
        fields = ['value', 'meaning', 'order', 'start_date', 'end_date', 'id']


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


class ObjectClassSpecialisationNarrowerClassSerializer(SubSerializer):

    class Meta:
        model = ObjectClassSpecialisationNarrowerClass
        fields = ['order', 'narrower_class']

