import graphene
from .aristotle_mdr import Query as AristotleMDRQuery
from .aristotle_dse import Query as AristotleDSEQuery
from .comet import Query as CometQuery
# from .user import SingleUserQuery
from graphene_django.debug import DjangoDebug

class AristotleQuery(AristotleDSEQuery, AristotleMDRQuery, CometQuery, graphene.ObjectType):
    "The query root of the Aristotle GraphQL API"
    pass
#     #debug = graphene.Field(DjangoDebug, name='__debug')

# class AristotleQuery(AristotleMDRQuery, AristotleDSEQuery, graphene.ObjectType):
    # "The query root of the Aristotle GraphQL API"
    # pass
    #debug = graphene.Field(DjangoDebug, name='__debug')

schema = graphene.Schema(query=AristotleQuery)
