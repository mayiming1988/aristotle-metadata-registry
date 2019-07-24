from aristotle_mdr_graphql.utils import type_from_concept_model
from aristotle_mdr_graphql.fields import AristotleConceptFilterConnectionField
from aristotle_glossary.models import GlossaryItem

GlossaryItemNode = type_from_concept_model(GlossaryItem)


class Query:
    glossary_items = AristotleConceptFilterConnectionField(GlossaryItemNode)
