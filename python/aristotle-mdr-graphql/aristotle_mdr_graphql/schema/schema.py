import graphene
from .aristotle_mdr import Query as AristotleMDRQuery
from .aristotle_dse import Query as AristotleDSEQuery
from .comet import Query as CometQuery
# from .user import SingleUserQuery
from django.conf import settings
from django.apps import apps
from aristotle_mdr_graphql.utils import type_from_model


class AristotleQuery(AristotleDSEQuery, AristotleMDRQuery, CometQuery, graphene.ObjectType):
    """The query root of the Aristotle GraphQL API"""
    pass


# Loop through the models and instantiate GraphQL Nodes:
for (app_label, model_name) in settings.EXTRA_GRAPHQL_SCHEMA_MODELS:
    type_from_model(apps.get_model(app_label, model_name))

schema = graphene.Schema(query=AristotleQuery)
