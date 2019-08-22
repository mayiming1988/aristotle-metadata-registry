from typing import Type, Union, List, Dict, Any, cast
from aristotle_mdr_graphql.types import AristotleObjectType, AristotleConceptObjectType
from aristotle_mdr.models import _concept
from graphene_django.types import DjangoObjectType
import graphene
from aristotle_mdr_graphql.resolvers import aristotle_resolver
from textwrap import dedent
from .aristotle_filterset_classes import ConceptFilterSet

# Type for filter fields
FFType = Union[List[str], Dict[str, List[str]]]
# Type for meta kwargs
KwargsType = Dict[str, Any]


def inline_type_from_model(model: Type,
                           filter_fields: FFType = None,
                           description: str = None,
                           meta_kwargs: KwargsType = {}
                           ) -> Type:
    """Create a regular node from a django model"""

    _filter_fields: FFType = []
    if filter_fields is not None:
        _filter_fields = filter_fields

    kwargs = dict(
        model=model,
        description=description or dedent(model.__doc__),
        filter_fields=_filter_fields,
        default_resolver=aristotle_resolver,
    )
    kwargs.update(meta_kwargs)

    meta_class = type('Meta', (object, ), kwargs)
    dynamic_class = type(model.__name__ + 'Node', (DjangoObjectType, ), dict(Meta=meta_class))
    return dynamic_class


def type_from_model(model: Type,
                    filter_fields: FFType = None,
                    filterset_class=None,
                    description: str = None,
                    meta_kwargs: Dict[str, Any] = {}
                    ) -> Type:
    """
    Create a relay node from a django model.
    You should pass a filter_fields parameter OR a filterset_class parameter, but not both at the same time.
    :param model: Model to query.
    :param filter_fields:
    :param filterset_class:
    :param description: String Documentation of the Model passed.
    :param meta_kwargs:
    :return:
    """

    _filter_fields: FFType = []
    if filter_fields is not None:
        _filter_fields = filter_fields

    kwargs = dict(
        model=model,
        description=description or dedent(model.__doc__),
        filter_fields=_filter_fields,
        filterset_class=filterset_class,
        interfaces=(graphene.relay.Node, ),
        default_resolver=aristotle_resolver,
    )
    kwargs.update(meta_kwargs)

    meta_class = type('Meta', (object, ), kwargs)
    dynamic_class = type(model.__name__ + 'Node', (AristotleObjectType, ), dict(Meta=meta_class))
    return dynamic_class


def type_from_concept_model(model: Type[_concept],
                            filter_fields: FFType = None,
                            filterset_class=ConceptFilterSet,
                            extra_filter_fields: FFType = None,
                            resolver=aristotle_resolver,
                            meta_kwargs: KwargsType = {},
                            ) -> Type:
    """
    Create a relay node from a concept with a custom base class for concept specific fields.
    You should pass a filter_fields parameter OR a filterset_class parameter, but not both at the same time.
    :param model: Model to query.
    :param filter_fields: Dictionary of fields to be used as filter parameters in GraphQL.
    :param filterset_class: By default we use the ConceptFilterSet class.
    :param extra_filter_fields:
    :param resolver: Query resolver to be used.
    :param meta_kwargs:
    :return: Type
    """
    assert issubclass(model, _concept)

    _filter_fields: Dict[str, List[str]] = {
        'name': ['exact', 'icontains', 'iexact'],
        'uuid': ['exact'],
    }

    # Assign _filter_fields from filter_fields arg if available
    if filter_fields:
        _filter_fields = filter_fields_to_dict(filter_fields)

    # Update existing filter fields from extra_filter_fields if available
    if extra_filter_fields:
        _filter_fields.update(filter_fields_to_dict(extra_filter_fields))

    meta_kwargs.update(dict(
        model=model,
        description=dedent(model.__doc__),
        filter_fields=_filter_fields,
        # filterset_class=filterset_class,
        interfaces=(graphene.relay.Node, ),
        default_resolver=resolver,
    ))

    meta_class = type('Meta', (object, ), meta_kwargs)
    dynamic_class = type(model.__name__ + 'Node', (AristotleConceptObjectType,), dict(Meta=meta_class))

    return dynamic_class


def filter_fields_to_dict(filter_fields: FFType) -> Dict[str, List[str]]:
    """If filter fields is in list form convert to dict form"""
    if type(filter_fields) is list:
        return {key: ['exact'] for key in filter_fields}
    else:
        filter_fields = cast(dict, filter_fields)  # Just so the type checker understands
        return filter_fields
