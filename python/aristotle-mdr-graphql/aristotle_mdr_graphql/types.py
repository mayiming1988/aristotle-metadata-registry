import graphene
import logging

from aristotle_mdr import models as mdr_models
from aristotle_mdr import perms
from aristotle_mdr.contrib.identifiers import models as ident_models
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

logger = logging.getLogger(__name__)

from aristotle_mdr_graphql import resolvers
from .filterset import IdentifierFilterSet

class AristotleObjectType(DjangoObjectType):

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = [] #'__all__'

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
    namespace_prefix = graphene.String()
    class Meta:
        model = ident_models.ScopedIdentifier
        default_resolver = resolvers.aristotle_resolver
        interfaces = (relay.Node, )

    def resolve_namespace_prefix(self, info):
        return self.namespace.shorthand_prefix


class AristotleConceptObjectType(DjangoObjectType):
    metadata_type = graphene.String()
    identifiers = DjangoFilterConnectionField(ScopedIdentifierNode, filterset_class=IdentifierFilterSet)

    class Meta:
        model = mdr_models._concept
        interfaces = (relay.Node, )
        filter_fields = '__all__'

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):

        # Default resolver is set in type_from_concept_model instead
        kwargs.update({
            # 'default_resolver': aristotle_resolver,
            'interfaces': (relay.Node, ),
            # 'filter_fields': ['name'],
        })
        super().__init_subclass_with_meta__(*args, **kwargs)

    def resolve_metadata_type(self, info, **kwargs):
        item = self.item
        out = "{}:{}".format(item._meta.app_label,item._meta.model_name)
        return out


# from graphene import Field, List
# from graphene_django.filter.utils import (
#     get_filtering_args_from_filterset,
#     get_filterset_class
# )
# from functools import partial

# class DjangoFilterField(Field):
#     '''
#     Custom field to use django-filter with graphene object types (without relay).
#     '''

#     def __init__(self, _type, fields=None, extra_filter_meta=None,
#                  filterset_class=None, *args, **kwargs):
#         _fields = _type._meta.filter_fields
#         _model = _type._meta.model
#         self.of_type = _type
#         self.fields = fields or _fields
#         meta = dict(model=_model, fields=self.fields)
#         if extra_filter_meta:
#             meta.update(extra_filter_meta)
#         self.filterset_class = get_filterset_class(filterset_class, **meta)
#         self.filtering_args = get_filtering_args_from_filterset(
#             self.filterset_class, _type)
#         kwargs.setdefault('args', {})
#         kwargs['args'].update(self.filtering_args)
#         super().__init__(List(_type), *args, **kwargs)

#     @staticmethod
#     def list_resolver(manager, filterset_class, filtering_args, root, info, *args, **kwargs):
#         filter_kwargs = {k: v for k,
#                          v in kwargs.items() if k in filtering_args}
#         qs = manager.get_queryset()
#         qs = filterset_class(data=filter_kwargs, queryset=qs).qs
#         return qs

#     def get_resolver(self, parent_resolver):
#         return partial(self.list_resolver, self.of_type._meta.model._default_manager,
#                       self.filterset_class, self.filtering_args)


