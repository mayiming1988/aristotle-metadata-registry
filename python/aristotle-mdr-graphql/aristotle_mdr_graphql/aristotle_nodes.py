import graphene
from graphene_django.types import DjangoObjectType
from aristotle_mdr.contrib.identifiers.models import ScopedIdentifier
from aristotle_mdr.contrib.custom_fields.models import CustomValue
from aristotle_mdr.models import Status
from aristotle_mdr_graphql import resolvers


class ScopedIdentifierNode(DjangoObjectType):
    namespace_prefix = graphene.String()

    class Meta:
        model = ScopedIdentifier
        default_resolver = resolvers.aristotle_resolver

    def resolve_namespace_prefix(self):
        return self.namespace.shorthand_prefix


class StatusNode(DjangoObjectType):
    state_name = graphene.String()

    class Meta:
        model = Status
        default_resolver = resolvers.aristotle_resolver


class CustomValueNode(DjangoObjectType):
    field_name = graphene.String()

    class Meta:
        model = CustomValue
        default_resolver = resolvers.aristotle_resolver

    def resolve_field_name(self):
        return self.field.name
