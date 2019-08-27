from aristotle_mdr_graphql.utils import get_dynamic_type_node_from_model
from aristotle_mdr_graphql.fields import AristotleConceptFilterConnectionField
from aristotle_mdr_graphql.aristotle_filterset_classes import ConceptFilterSet
from aristotle_mdr_graphql.types import AristotleConceptObjectType
from aristotle_glossary.models import GlossaryItem

GlossaryItemNode = get_dynamic_type_node_from_model(
    model=GlossaryItem,
    filterset_class=ConceptFilterSet,
    object_type=AristotleConceptObjectType,
)


class Query:
    glossary_items = AristotleConceptFilterConnectionField(GlossaryItemNode)
