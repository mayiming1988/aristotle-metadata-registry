from typing import Type, Union, List, Dict, Any, cast
from aristotle_mdr_graphql.types import AristotleObjectType, AristotleConceptObjectType
from aristotle_mdr.models import _concept
import graphene
from aristotle_mdr_graphql.resolvers import aristotle_resolver
from textwrap import dedent
from .aristotle_filterset_classes import ConceptFilterSet

FFType = Union[List[str], Dict[str, List[str]]]  # Type for filter fields
KwargsType = Dict[str, Any]  # Type for meta kwargs


def get_dynamic_type_node_from_model(model: Type = None,
                                     description: str = None,
                                     filterset_class=None,
                                     filter_fields=None,
                                     default_resolver=aristotle_resolver,
                                     interfaces=None,
                                     meta_kwargs=None,
                                     object_type=None,
                                     ) -> Type:
    """
    This generic function creates a type node from a Model Object dynamically.
    Some default kwarg values are provided for the most common cases.
    Values can be overridden, but there is an important thing to consider:
    ** Only can be passed a filterset_class kwarg OR a filter_fields kwarg. **
    :param model: Base model to create the node.
    :param description: Description used in the GraphQl interface.
    :param filterset_class: Subclass of Django filterset.
    :param filter_fields: Fields to be used as parameters to filter content in the query.
    :param default_resolver: Query Resolver.
    :param interfaces: Iterable. Default interface is the graphene relay Node.
    :param meta_kwargs:
    :param object_type:
    :return:
    """

    if filter_fields is None:
        filter_fields = {}
    if meta_kwargs is None:
        meta_kwargs = {}
    if interfaces is None:
        interfaces = [graphene.relay.Node]  # Use graphene relay Node as the default interface.
    if object_type is None:
        object_type = AristotleObjectType  # Use AristotleObjectType as the default object_type.

    meta_kwargs.update(
        {
            "model": model,
            "description": description or dedent(model.__doc__),
            "filterset_class": filterset_class,
            "filter_fields": convert_filter_fields_list_to_dict(filter_fields),
            "interfaces": interfaces,
            "default_resolver": default_resolver,
        }
    )

    meta_class = type('Meta', (object,), meta_kwargs)
    return type(model.__name__ + 'Node', (object_type,), dict(Meta=meta_class))


def get_dynamic_type_node_from_concept_model(**kwargs):
    """
    This generic function dynamically creates a type node from an Object which subclasses from "_concept".
    The purpose of this function is to save lines of code providing a useful tool for the most-common scenario:
    creating a type node from a Model subclassed from _concept.
    Please use get_dynamic_type_node_from_model() if you require more flexibility.
    """

    assert issubclass(kwargs.get("model"), _concept)

    if "filterset_class" in kwargs or "object_type" in kwargs:
        raise ValueError("get_dynamic_type_node_from_concept_model() uses default values for filterset_class and object_type parameters."
                         "If you need more flexibility please use 'get_dynamic_type_node_from_model()' instead")

    return get_dynamic_type_node_from_model(filterset_class=ConceptFilterSet, object_type=AristotleConceptObjectType, **kwargs)


def convert_filter_fields_list_to_dict(filter_fields: FFType) -> Dict[str, List[str]]:
    """If filter fields is in list form convert to dict form"""
    if type(filter_fields) is list:
        return {key: ['exact'] for key in filter_fields}
    else:
        filter_fields = cast(dict, filter_fields)  # Just so the type checker understands
        return filter_fields
