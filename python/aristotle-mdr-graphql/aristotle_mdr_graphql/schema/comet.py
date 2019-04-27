from aristotle_mdr_graphql.fields import AristotleConceptFilterConnectionField, AristotleFilterConnectionField
from comet import models as comet_models
from aristotle_mdr_graphql.utils import type_from_concept_model, type_from_model, inline_type_from_model
from graphene_django.filter import DjangoFilterConnectionField

IndicatorNode = type_from_concept_model(comet_models.Indicator)
# IndicatorSetTypeNode = type_from_model(comet_models.IndicatorSetType)
IndicatorSetNode = type_from_concept_model(comet_models.IndicatorSet)
OutcomeAreaNode = type_from_concept_model(comet_models.OutcomeArea)
QualityStatementNode = type_from_concept_model(comet_models.QualityStatement)
# FrameworkNode = type_from_concept_model(comet_models.Framework)
IndicatorNumeratorDefinitionNode = type_from_model(comet_models.IndicatorNumeratorDefinition)
IndicatorDenominatorDefinitionNode = type_from_model(comet_models.IndicatorDenominatorDefinition)
IndicatorDisaggregationDefinitionNode = type_from_model(comet_models.IndicatorDisaggregationDefinition)


class Query(object):

    indicators = AristotleConceptFilterConnectionField(IndicatorNode)
    indicator_sets = AristotleConceptFilterConnectionField(IndicatorSetNode)
    # indicator_set_types = AristotleFilterConnectionField(IndicatorSetTypeNode)
    outcome_areas = AristotleConceptFilterConnectionField(OutcomeAreaNode)
    quality_statements = AristotleConceptFilterConnectionField(QualityStatementNode)
    # frameworks = AristotleConceptFilterConnectionField(FrameworkNode)
    indicator_numerator_definitions = DjangoFilterConnectionField(IndicatorNumeratorDefinitionNode)
    indicator_denominator_definitions = DjangoFilterConnectionField(IndicatorDenominatorDefinitionNode)
    indicator_disaggregation_definitions = DjangoFilterConnectionField(IndicatorDisaggregationDefinitionNode)
