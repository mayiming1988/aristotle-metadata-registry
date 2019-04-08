from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _

import aristotle_mdr.models as MDR
from aristotle_mdr.fields import ConceptForeignKey, ConceptManyToManyField
import aristotle_dse.models as aristotle_dse
from aristotle_mdr.utils.model_utils import (
    ManagedItem,
    aristotleComponent,
)


class IndicatorType(ManagedItem):
    class Meta:
        verbose_name = "Indicator Type"

# Subclassing from DataElement causes indicators to present as DataElements, which isn't quite right.


class Indicator(MDR.concept):
    """
    An indicator is a single measure that is reported on regularly
    and that provides relevant and actionable information about population or system performance.
    """
    backwards_compatible_fields = ['representation_class']

    template = "comet/indicator.html"
    outcome_areas = ConceptManyToManyField('OutcomeArea', related_name="indicators", blank=True)
    indicator_type = models.ForeignKey(IndicatorType, blank=True, null=True)


    computation_description = MDR.RichTextField(blank=True)
    computation = MDR.RichTextField(blank=True)

    numerator_description = MDR.RichTextField(blank=True)
    numerator_computation = models.TextField(blank=True)

    denominator_description = MDR.RichTextField(blank=True)
    denominator_computation = models.TextField(blank=True)

    disaggregation_description = MDR.RichTextField(blank=True)

    rationale = MDR.RichTextField(blank=True)
    benchmark = MDR.RichTextField(blank=True)
    reporting_information = MDR.RichTextField(blank=True)

    serialize_weak_entities = [
        ('numerators', 'indicatornumeratordefinition_set'),
        ('denominators', 'indicatordenominatordefinition_set'),
        ('disaggregators', 'indicatordisaggregationdefinition_set'),
    ]
    clone_fields = ['indicatornumeratordefinition', 'indicatordenominatordefinition', 'indicatordisaggregationdefinition']


    def add_component(self, model_class, **kwargs):
        kwargs.pop('indicator', None)
        from django.db.models import Max
        max_order = list(
            model_class.objects.filter(indicator=self)
            .annotate(latest=Max('order')).values_list('order', flat=True)
        )
        if not max_order:
            order = 1
        else:
            order = max_order[0] + 1
        return model_class.objects.create(indicator=self, order=order, **kwargs)

    @property
    def numerators(self):
        return MDR.DataElement.objects.filter(
            indicatornumeratordefinition__indicator=self
        )

    def add_numerator(self, **kwargs):
        self.add_component(model_class=IndicatorNumeratorDefinition, **kwargs)

    @property
    def denominators(self):
        return MDR.DataElement.objects.filter(
            indicatordenominatordefinition__indicator=self
        )

    def add_denominator(self, **kwargs):
        self.add_component(model_class=IndicatorDenominatorDefinition, **kwargs)

    @property
    def disaggregators(self):
        return MDR.DataElement.objects.filter(
            indicatordisaggregationdefinition__indicator=self
        )

    def add_disaggregator(self, **kwargs):
        self.add_component(model_class=IndicatorDisaggregationDefinition, **kwargs)


class IndicatorDataElementBase(aristotleComponent):
    class Meta:
        abstract=True
        ordering = ['order']

    indicator = ConceptForeignKey(Indicator)
    order = models.PositiveSmallIntegerField(
        "Order",
        help_text=_("The position of this data element in the indicator")
    )
    description = MDR.RichTextField(blank=True)
    guide_for_use = MDR.RichTextField(blank=True)
    data_element = ConceptForeignKey(MDR.DataElement, blank=True, null=True)
    data_set_specification = ConceptForeignKey(aristotle_dse.DataSetSpecification, blank=True, null=True)
    data_set = ConceptForeignKey(aristotle_dse.Dataset, blank=True, null=True)

    inline_field_layout = 'list'

    @property
    def parentItem(self):
        return self.indicator


class IndicatorNumeratorDefinition(IndicatorDataElementBase):
    pass


class IndicatorDenominatorDefinition(IndicatorDataElementBase):
    pass


class IndicatorDisaggregationDefinition(IndicatorDataElementBase):
    pass


class IndicatorSetType(ManagedItem):
    pass


class IndicatorSet(MDR.concept):
    template = "comet/indicatorset.html"
    indicator_set_type = models.ForeignKey(IndicatorSetType, blank=True, null=True)


class IndicatorInclusion(aristotleComponent):
    order = models.PositiveSmallIntegerField(
        "Order",
        help_text=_("The position of this indicator in the set")
    )
    indicator_set = ConceptForeignKey(IndicatorSet)
    indicator = ConceptForeignKey(Indicator, blank=True, null=True)
    name = models.CharField(
        max_length=1024, blank=True,
        help_text=_("The name identifying this indicator in the set")
    )

    class Meta:
        ordering = ['order']

    @property
    def parentItem(self):
        return self.indicator_set


class OutcomeArea(MDR.concept):
    template = "comet/outcomearea.html"


class QualityStatement(MDR.concept):
    template = "comet/qualitystatement.html"
    timeliness = MDR.RichTextField(blank=True)
    accessibility = MDR.RichTextField(blank=True)
    interpretability = MDR.RichTextField(blank=True)
    relevance = MDR.RichTextField(blank=True)
    accuracy = MDR.RichTextField(blank=True)
    coherence = MDR.RichTextField(blank=True)


class Framework(MDR.concept):
    template = "comet/framework.html"
    parentFramework = ConceptForeignKey('Framework', blank=True, null=True, related_name="childFrameworks")
    indicators = ConceptManyToManyField(Indicator, related_name="frameworks", blank=True)
