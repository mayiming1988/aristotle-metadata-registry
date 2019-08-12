import logging
from graphene import relay, String as graphene_string
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.custom_fields import models as cf_models
from aristotle_mdr.contrib.identifiers import models as ident_models
from graphene_django.types import DjangoObjectType
from aristotle_mdr_graphql import resolvers
from .aristotle_filterset_classes import IdentifierFilterSet, StatusFilterSet, ConceptFilterSet
from .fields import DjangoListFilterField, ObjectField

logger = logging.getLogger(__name__)


class AristotleObjectType(DjangoObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = []  # type: ignore

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):

        kwargs.update({
            'default_resolver': resolvers.aristotle_resolver,
            'interfaces': (relay.Node, ),
        })
        if "filter_fields" not in kwargs.keys():
            kwargs['filter_fields'] = '__all__'
        super().__init_subclass_with_meta__(*args, **kwargs)


class ScopedIdentifierNode(DjangoObjectType):
    namespace_prefix = graphene_string()

    class Meta:
        model = ident_models.ScopedIdentifier
        default_resolver = resolvers.aristotle_resolver
        # interfaces = (relay.Node, )

    def resolve_namespace_prefix(self):
        return self.namespace.shorthand_prefix


class CustomValueNode(DjangoObjectType):
    field_name = graphene_string()

    class Meta:
        model = cf_models.CustomValue
        default_resolver = resolvers.aristotle_resolver
        # interfaces = (relay.Node, )

    def resolve_field_name(self):
        return self.field.name


class StatusNode(DjangoObjectType):
    state_name = graphene_string()

    class Meta:
        model = mdr_models.Status
        default_resolver = resolvers.aristotle_resolver


class AristotleConceptObjectType(DjangoObjectType):
    aristotle_id = graphene_string()
    metadata_type = graphene_string()
    identifiers = DjangoListFilterField(ScopedIdentifierNode, filterset_class=IdentifierFilterSet)
    statuses = DjangoListFilterField(StatusNode, filterset_class=StatusFilterSet)
    custom_values_as_object = ObjectField()
    slots_as_object = ObjectField()

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        # filter_fields = '__all__'
        # filterset_class = ConceptFilterSet

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):

        # Default resolver is set in type_from_concept_model instead
        kwargs.update({
            # 'default_resolver': aristotle_resolver,
            'interfaces': (relay.Node, ),
            # 'filter_fields': ['name'],
        })
        super().__init_subclass_with_meta__(*args, **kwargs)

    # TODO: REMOVE THESE METHODS BECAUSE THEY ARE NOT BEING USED ANYWHERE.
    # def resolve_metadata_type(self):
    #     return "{}:{}".format(self.item._meta.app_label, self.item._meta.model_name)

    # def resolve_custom_values_as_object(self, info):
    #     out = {}
    #     for val in cf_models.CustomValue.objects.get_item_allowed(self.item, info.context.user):
    #         out[val.field.name] = {
    #             "type": val.field.type,
    #             "value": val.content
    #         }
    #     return out
    #
    # def resolve_slots_as_object(self, info):
    #     out = {}
    #     for slot in slots_models.Slot.objects.get_item_allowed(self.item, info.context.user):
    #         out[slot.name] = {
    #             "type": slot.type,
    #             "value": slot.value
    #         }
    #     return out

