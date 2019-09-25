from graphene_django.types import DjangoObjectType
from comet import models as comet_models
from aristotle_mdr_graphql.utils import get_dynamic_type_node_from_model, get_dynamic_type_node_from_concept_model
from aristotle_mdr_graphql.fields import AristotleConceptFilterConnectionField, AristotleFilterConnectionField

IndicatorNode = get_dynamic_type_node_from_concept_model(model=comet_models.Indicator)
IndicatorSetNode = get_dynamic_type_node_from_concept_model(model=comet_models.IndicatorSet)
IndicatorInclusionNode = get_dynamic_type_node_from_model(
    model=comet_models.IndicatorInclusion,
    interfaces=[],  # We are overriding the default interface.
    object_type=DjangoObjectType,  # We are also overriding the Object Type.
)
OutcomeAreaNode = get_dynamic_type_node_from_concept_model(model=comet_models.OutcomeArea)
QualityStatementNode = get_dynamic_type_node_from_concept_model(model=comet_models.QualityStatement)
FrameworkNode = get_dynamic_type_node_from_concept_model(model=comet_models.Framework)
FrameworkDimensionNode = get_dynamic_type_node_from_model(
    model=comet_models.FrameworkDimension,
    meta_kwargs={'exclude_fields': ['lft', 'rght', 'tree_id']},
)
IndicatorNumeratorDefinitionNode = get_dynamic_type_node_from_model(model=comet_models.IndicatorNumeratorDefinition)
IndicatorDenominatorDefinitionNode = get_dynamic_type_node_from_model(model=comet_models.IndicatorDenominatorDefinition)
IndicatorDisaggregationDefinitionNode = get_dynamic_type_node_from_model(
    model=comet_models.IndicatorDisaggregationDefinition)


class Query:
    framework_dimensions = AristotleFilterConnectionField(FrameworkDimensionNode)
    indicators = AristotleConceptFilterConnectionField(IndicatorNode)
    indicator_sets = AristotleConceptFilterConnectionField(IndicatorSetNode)
    outcome_areas = AristotleConceptFilterConnectionField(OutcomeAreaNode)
    quality_statements = AristotleConceptFilterConnectionField(QualityStatementNode)
    frameworks = AristotleConceptFilterConnectionField(FrameworkNode)
