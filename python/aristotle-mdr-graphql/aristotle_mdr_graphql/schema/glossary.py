from aristotle_mdr_graphql.utils import type_from_model
from aristotle_mdr_graphql.fields import AristotleFilterConnectionField
from aristotle_glossary.models import GlossaryItem

GlossaryItemNode = type_from_model(GlossaryItem)


class Query:
    glossary_items = AristotleFilterConnectionField(GlossaryItemNode)
