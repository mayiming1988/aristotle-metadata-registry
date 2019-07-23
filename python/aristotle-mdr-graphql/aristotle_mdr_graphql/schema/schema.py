from typing import List, Type
import graphene
from .aristotle_mdr import Query as AristotleMDRQuery
from .aristotle_dse import Query as AristotleDSEQuery
from .glossary import Query as GlossaryQuery
from .comet import Query as CometQuery
# from .user import SingleUserQuery
from django.conf import settings
from django.utils.module_loading import import_string
from django.apps import apps
from aristotle_mdr_graphql.utils import type_from_model

import logging
logger = logging.getLogger(__name__)

# Query objects to create root query from
QUERY_OBJECTS = [
    AristotleDSEQuery,
    AristotleMDRQuery,
    CometQuery,
    GlossaryQuery,
]

# Loop through the models and instantiate GraphQL Nodes:
for imp in settings.EXTRA_GRAPHQL_SCHEMA_MODELS:
    logger.warning('Importing: {imp}'.format(imp=imp))
    try:
        import_string(imp)
    except ImportError:
        logger.warning('Could not import {}'.format(imp))


def get_query_model(bases: List[Type]) -> Type:
    """Create the root level query objects from sub query objects"""

    for imp in settings.EXTRA_GRAPHQL_QUERY_OBJS:
        logger.warning('Importing: {imp}'.format(imp=imp))
        try:
            query = import_string(imp)
        except ImportError:
            logger.warning('Could not import {}'.format(imp))
            query = None

        if query:
            bases.append(query)

    bases.append(graphene.ObjectType)
    return type('AristotleQuery', tuple(QUERY_OBJECTS), {})


# The query root of the Aristotle GraphQL API
AristotleQuery = get_query_model(QUERY_OBJECTS)

schema = graphene.Schema(query=AristotleQuery)
