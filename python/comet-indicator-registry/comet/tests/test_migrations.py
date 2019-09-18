from aristotle_mdr import models
from aristotle_mdr.contrib.slots import models as slots_models
from aristotle_mdr.models import STATES
from aristotle_mdr.tests.migrations import MigrationsTestCase
from aristotle_mdr.utils import migrations as migration_utils

from django.test import TestCase, tag
from django.apps import apps as current_apps
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest import skip


class TestSixToEightMigration(MigrationsTestCase, TestCase):

    app = 'comet'
    migrate_from = [
        ('aristotle_mdr','0045__concept_superseded_by_items'),
        ('comet','0005_auto_20181107_0433'),
    ]
    migrate_to = '0008_auto_20190218_0404'

    def setUpBeforeMigration(self, apps):

        Indicator = apps.get_model('comet', 'Indicator')
        IndicatorSet = apps.get_model('comet', 'IndicatorSet')
        IndicatorType = apps.get_model('comet', 'IndicatorType')
        IndicatorSetType = apps.get_model('comet', 'IndicatorSetType')
        de = apps.get_model('aristotle_mdr', 'DataElement')

        self.indicatorsettype = IndicatorSetType.objects.create(
            name='Indicator Set Type 1',
            definition='test defn',
        )

        self.indicatorset = IndicatorSet.objects.create(
            name='Indicator Set 1',
            definition='test defn',
            indicatorSetType = self.indicatorsettype
        )

        self.indicatortype = IndicatorType.objects.create(
            name='Indicator Type 1',
            definition='test defn',
        )

        self.indicator = Indicator.objects.create(
            name='Indicator 1',
            definition='test defn',
            indicatorType = self.indicatortype
        )

        self.de1 = de.objects.create(
            name='DE1',
            definition='test defn',
        )

        self.de2 = de.objects.create(
            name='DE2',
            definition='test defn',
        )

        self.de3 = de.objects.create(
            name='DE3',
            definition='test defn',
        )

        self.indicatorset.indicators.add(self.indicator)

        self.indicator.numerators.add(self.de1)
        self.indicator.denominators.add(self.de2)
        self.indicator.disaggregators.add(self.de3)

    def test_migration(self):

        Indicator = self.apps.get_model('comet', 'Indicator')
        IndicatorType = self.apps.get_model('comet', 'IndicatorType')

        de = self.apps.get_model('aristotle_mdr', 'DataElement')
        numerator_model = self.apps.get_model('comet', 'IndicatorNumeratorDefinition')
        denominator_model = self.apps.get_model('comet', 'IndicatorDenominatorDefinition')
        disaggregation_model = self.apps.get_model('comet', 'IndicatorDisaggregationDefinition')

        indicator_obj = Indicator.objects.get(pk=self.indicator.pk)
        numerators_list = numerator_model.objects.filter(indicator=indicator_obj)
        denominators_list = denominator_model.objects.filter(indicator=indicator_obj)
        disaggregators_list = disaggregation_model.objects.filter(indicator=indicator_obj)
        
        self.assertEqual(1, numerators_list.count())
        self.assertEqual(self.de1.id, numerators_list.first().data_element_id)

        self.assertEqual(1, denominators_list.count())
        self.assertEqual(self.de2.id, denominators_list.first().data_element_id)

        self.assertEqual(1, disaggregators_list.count())
        self.assertEqual(self.de3.id, disaggregators_list.first().data_element_id)

        # Do indicator sets now

        IndicatorSet = self.apps.get_model('comet', 'IndicatorSet')
        inclusion_model = self.apps.get_model('comet', 'IndicatorInclusion')

        indicatorset_obj = IndicatorSet.objects.get(pk=self.indicatorset.pk)

        indicators_list = inclusion_model.objects.filter(indicator_set=indicatorset_obj)

        self.assertEqual(1, indicators_list.count())
        self.assertEqual(self.indicator.id, indicators_list.first().indicator_id)

        # Do indicator types now

        IndicatorType = self.apps.get_model('comet', 'IndicatorType')
        ind_type = IndicatorType.objects.get(pk=self.indicatortype.pk)

        self.assertEqual(indicator_obj.indicator_type_id, ind_type.pk)


        # Do indicator set types now

        IndicatorSetType = self.apps.get_model('comet', 'IndicatorSetType')
        ind_set_type = IndicatorSetType.objects.get(pk=self.indicatorsettype.pk)

        self.assertEqual(indicatorset_obj.indicator_set_type_id, ind_set_type.pk)
