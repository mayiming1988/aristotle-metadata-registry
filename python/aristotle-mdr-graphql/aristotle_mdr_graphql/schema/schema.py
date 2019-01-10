import graphene
from .aristotle_mdr import Query as AristotleMDRQuery
from .aristotle_dse import Query as AristotleDSEQuery
from .comet import Query as CometQuery
# from .user import SingleUserQuery


class AristotleQuery(AristotleDSEQuery, AristotleMDRQuery, CometQuery, graphene.ObjectType):
    "The query root of the Aristotle GraphQL API"


schema = graphene.Schema(query=AristotleQuery)
