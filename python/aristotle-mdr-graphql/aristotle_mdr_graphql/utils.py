from typing import Type, Union, List, Dict, Optional, Any, cast
from aristotle_mdr_graphql.types import AristotleObjectType, AristotleConceptObjectType
from aristotle_mdr.models import _concept
from graphene_django.types import DjangoObjectType
import graphene
from aristotle_mdr_graphql.resolvers import aristotle_resolver
from textwrap import dedent

# Type for filter fields
FFType = Union[List[str], Dict[str, List[str]]]
# Type for meta kwargs
KwargsType = Dict[str, Any]


def inline_type_from_model(meta_model: Type, filter_fields: FFType=None,
                           description: str=None, meta_kwargs: KwargsType={}) -> Type:
    """Create a regular node from a django model"""

    new_model_name = meta_model.__name__ + 'Node'
    description = description or dedent(meta_model.__doc__)

    _filter_fields: FFType = []
    if filter_fields is not None:
        _filter_fields = filter_fields

    kwargs = dict(
        model=meta_model,
        description=description,
        filter_fields=_filter_fields,
        default_resolver=aristotle_resolver,
    )
    kwargs.update(meta_kwargs)

    meta_class = type('Meta', (object, ), kwargs)
    dynamic_class = type(new_model_name, (DjangoObjectType, ), dict(Meta=meta_class))
    return dynamic_class


def type_from_model(meta_model: Type, filter_fields: FFType=None,
                    description: str=None, meta_kwargs: Dict[str, Any]={}) -> Type:
    """Create a relay node from a django model"""

    new_model_name = meta_model.__name__ + 'Node'
    description = description or dedent(meta_model.__doc__)

    _filter_fields: FFType = []
    if filter_fields is not None:
        _filter_fields = filter_fields

    kwargs = dict(
        model=meta_model,
        description=description,
        filter_fields=_filter_fields,
        interfaces=(graphene.relay.Node, ),
        default_resolver=aristotle_resolver,
    )
    kwargs.update(meta_kwargs)

    meta_class = type('Meta', (object, ), kwargs)
    dynamic_class = type(new_model_name, (AristotleObjectType, ), dict(Meta=meta_class))
    return dynamic_class


def filter_fields_to_dict(filter_fields: FFType) -> Dict[str, List[str]]:
    """If filter fields is in list form convert to dict form"""
    if type(filter_fields) is list:
        return {key: ['exact'] for key in filter_fields}
    else:
        filter_fields = cast(dict, filter_fields)  # Just so the type checker understands
        return filter_fields


def type_from_concept_model(meta_model: Type[_concept], filter_fields: FFType=None, extra_filter_fields: FFType=None,
                            resolver=aristotle_resolver, meta_kwargs: KwargsType={}) -> Type:
    """Create a relay node from a concept with a custom base class for concept specific fields"""
    assert issubclass(meta_model, _concept)

    new_model_name = meta_model.__name__ + 'Node'
    description = dedent(meta_model.__doc__)
    _filter_fields: Dict[str, List[str]] = {
        'name': ['exact', 'icontains', 'iexact'],
        'uuid': ['exact'],
    }

    # Assign _filter_fields from filter_fields arg if avaliable
    if filter_fields:
        _filter_fields = filter_fields_to_dict(filter_fields)

    # Update existing filter fields from extra_filter_fields if avaliable
    if extra_filter_fields:
        _filter_fields.update(filter_fields_to_dict(extra_filter_fields))

    meta_kwargs.update(dict(
        model=meta_model,
        description=description,
        filter_fields=_filter_fields,
        interfaces=(graphene.relay.Node, ),
        default_resolver=resolver,
    ))

    meta_class = type('Meta', (object, ), meta_kwargs)
    dynamic_class = type(new_model_name, (AristotleConceptObjectType, ), dict(Meta=meta_class))

    return dynamic_class
