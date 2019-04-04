import comet
import reversion
from django.contrib import admin
from aristotle_mdr.register import register_concept

register_concept(comet.models.IndicatorSet)
register_concept(comet.models.OutcomeArea)

register_concept(comet.models.Indicator,
    extra_fieldsets = [
        ('Metadata', {'fields': ['outcome_areas','indicator_type']}),
        # ('Components', {'fields': ['dataElementConcept','valueDomain']}),
        # ('Computation', {'fields': ['numerators','denominators','disaggregators']}),
    ],
    reversion={
        'follow': ['indicatornumeratordefinition_set', 'indicatordenominatordefinition_set', 'indicatordisaggregationdefinition_set'],
        'follow_classes': [
            comet.models.IndicatorNumeratorDefinition,
            comet.models.IndicatorDenominatorDefinition,
            comet.models.IndicatorDisaggregationDefinition,
        ]
    },
)


register_concept(comet.models.QualityStatement,
    extra_fieldsets = [
        ('Data Quality Guidelines',
            {'fields': ['timeliness','accessibility','interpretability','relevance','accuracy','coherence']}
        ),
    ]
)


register_concept(comet.models.Framework,
    extra_fieldsets = [
        ('Data Quality Guidelines', {'fields': ['parentFramework','indicators']}),
    ]
)

# admin.site.register(comet.models.IndicatorSetType)
# admin.site.register(comet.models.IndicatorType)

# reversion.revisions.register(comet.models.IndicatorSetType)
# reversion.revisions.register(comet.models.IndicatorType)
