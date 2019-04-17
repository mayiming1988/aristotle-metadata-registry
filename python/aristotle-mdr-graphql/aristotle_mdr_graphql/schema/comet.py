from aristotle_mdr_graphql.fields import AristotleConceptFilterConnectionField
from comet import models as comet_models
from aristotle_mdr_graphql.utils import type_from_concept_model

IndicatorNode = type_from_concept_model(comet_models.Indicator)
# IndicatorSetNode = type_from_concept_model(comet_models.IndicatorSet)
# OutcomeAreaNode = type_from_concept_model(comet_models.OutcomeArea)
# QualityStatementNode = type_from_concept_model(comet_models.QualityStatement)
# FrameworkNode = type_from_concept_model(comet_models.Framework)


class Query(object):

    indicators = AristotleConceptFilterConnectionField(IndicatorNode)
    # indicator_sets = AristotleConceptFilterConnectionField(IndicatorSetNode)
    # outcome_areas = AristotleConceptFilterConnectionField(OutcomeAreaNode)
    # quality_statements = AristotleConceptFilterConnectionField(QualityStatementNode)
    # frameworks = AristotleConceptFilterConnectionField(FrameworkNode)
