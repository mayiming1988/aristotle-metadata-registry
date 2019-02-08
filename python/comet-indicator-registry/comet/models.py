from __future__ import unicode_literals

from django.db import models

from aristotle_mdr.models import RichTextField
import aristotle_mdr as aristotle
from aristotle_mdr.fields import ConceptForeignKey, ConceptManyToManyField
import aristotle_dse.models as aristotle_dse


class IndicatorType(aristotle.models.concept):
    pass


# Subclassing from DataElement causes indicators to present as DataElements, which isn't quite right.


class Indicator(aristotle.models.concept):
    """
    An indicator is a single measure that is reported on regularly
    and that provides relevant and actionable information about population or system performance.
    """
    template = "comet/indicator.html"
    dataElementConcept=ConceptForeignKey(
        aristotle.models.DataElementConcept,
        verbose_name="Data Element Concept",
        blank=True,
        null=True
    )
    valueDomain=ConceptForeignKey(
        aristotle.models.ValueDomain,
        verbose_name="Value Domain",
        blank=True,
        null=True
    )
    outcome_areas = ConceptManyToManyField('OutcomeArea', related_name="indicators", blank=True)

    indicatorType = ConceptForeignKey(IndicatorType, blank=True, null=True)
    numerators = ConceptManyToManyField(
        aristotle.models.DataElement,
        related_name="as_numerator",
        blank=True
    )
    denominators = ConceptManyToManyField(
        aristotle.models.DataElement,
        related_name="as_denominator",
        blank=True
    )
    disaggregators = ConceptManyToManyField(
        aristotle.models.DataElement,
        related_name="as_disaggregator",
        blank=True
    )

    numerator_description = models.TextField(blank=True)
    numerator_computation = models.TextField(blank=True)
    denominator_description = models.TextField(blank=True)
    denominator_computation = models.TextField(blank=True)
    computationDescription = RichTextField(blank=True)
    rationale = RichTextField(blank=True)
    disaggregation_description = RichTextField(blank=True)

    related_objects = [
        'dataElementConcept',
        'valueDomain'
    ]


class IndicatorDataElementBase(aristotle.models.aristotleComponent):
    class Meta:
        abstract=True
        ordering = ['order']

    indicator = ConceptForeignKey(Indicator)
    description = RichTextField()
    data_element = ConceptForeignKey(aristotle.models.DataElement)
    data_set_specification = ConceptForeignKey(aristotle_dse.DataSetSpecification)
    data_set = ConceptForeignKey(aristotle_dse.Dataset)

    @property
    def parentItem(self):
        return self.indicator_set    


class IndicatorSetType(aristotle.models.unmanagedObject):
    pass


class IndicatorSet(aristotle.models.concept):
    template = "comet/indicatorset.html"
    # indicators = ConceptManyToManyField(Indicator, related_name="indicatorSets", blank=True, null=True)
    indicatorSetType = models.ForeignKey(IndicatorSetType, blank=True, null=True)


class IndicatorInclusion(aristotle.models.aristotleComponent):
    indicator_set = ConceptForeignKey(IndicatorSet)
    indicator = ConceptForeignKey(Indicator, blank=True, null=True)
    name = models.CharField(
        max_length=1024, blank=True,
        help_text=_("The name identifying this indicator in the set")
    )

    @property
    def parentItem(self):
        return self.indicator_set


class OutcomeArea(aristotle.models.concept):
    template = "comet/outcomearea.html"


class QualityStatement(aristotle.models.concept):
    template = "comet/qualitystatement.html"
    timeliness = RichTextField(blank=True)
    accessibility = RichTextField(blank=True)
    interpretability = RichTextField(blank=True)
    relevance = RichTextField(blank=True)
    accuracy = RichTextField(blank=True)
    coherence = RichTextField(blank=True)
    implementationStartDate = models.DateField(blank=True, null=True)
    implementationEndDate = models.DateField(blank=True, null=True)


class Framework(aristotle.models.concept):
    template = "comet/framework.html"
    parentFramework = ConceptForeignKey('Framework', blank=True, null=True, related_name="childFrameworks")
    indicators = ConceptManyToManyField(Indicator, related_name="frameworks", blank=True)