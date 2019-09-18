import logging
import graphene
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.custom_fields import models as cf_models
from aristotle_mdr.contrib.slots import models as slots_models
from graphene_django.types import DjangoObjectType
from aristotle_mdr_graphql import resolvers
from .aristotle_filterset_classes import IdentifierFilterSet, StatusFilterSet
from .fields import DjangoListFilterField, ObjectField
from .aristotle_nodes import StatusNode, ScopedIdentifierNode

logger = logging.getLogger(__name__)


class AristotleObjectType(DjangoObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (graphene.relay.Node, )

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):

        kwargs.update({
            'default_resolver': resolvers.aristotle_resolver,
            'interfaces': (graphene.relay.Node, ),
        })
        # if "filter_fields" not in kwargs.keys():
        #     kwargs['filter_fields'] = '__all__'
        super().__init_subclass_with_meta__(*args, **kwargs)


class AristotleConceptObjectType(DjangoObjectType):
    aristotle_id = graphene.String()
    metadata_type = graphene.String()
    identifiers = DjangoListFilterField(ScopedIdentifierNode, filterset_class=IdentifierFilterSet)
    statuses = DjangoListFilterField(StatusNode, filterset_class=StatusFilterSet)
    custom_values_as_object = ObjectField()
    slots_as_object = ObjectField()

    class Meta:
        model = mdr_models._concept
        interfaces = (graphene.relay.Node, )
        # filter_fields = '__all__'
        # filterset_class = ConceptFilterSet

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):

        kwargs.update({
            'interfaces': (graphene.relay.Node, ),
        })
        super().__init_subclass_with_meta__(*args, **kwargs)

    # Important info: the following methods are actually used by GraphQL to resolve the queries:
    # "customValuesAsObject", "metadataType" and "slotsAsObject".
    def resolve_metadata_type(self, info, **kwargs):  # Parameters "info" and "kwargs" are used by the graphene api.
        return "{}:{}".format(self.item._meta.app_label, self.item._meta.model_name)

    def resolve_custom_values_as_object(self, info, **kwargs):  # Parameter "kwargs" is used by the graphene api.
        out = {}
        for val in cf_models.CustomValue.objects.get_item_allowed(self.item, info.context.user):
            out[val.field.name] = {
                "type": val.field.type,
                "value": val.content
            }
        return out

    def resolve_slots_as_object(self, info, **kwargs):  # Parameter "kwargs" is used by the graphene api.
        out = {}
        for slot in slots_models.Slot.objects.get_item_allowed(self.item, info.context.user):
            out[slot.name] = {
                "type": slot.type,
                "value": slot.value
            }
        return out


