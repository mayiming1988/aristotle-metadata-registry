from django.test import TestCase, tag
from django.urls import reverse

from aristotle_mdr.tests.utils import ManagedObjectVisibility, model_to_dict_with_change_time
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept

from aristotle_mdr import models as MDR
from comet import models


def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0)


class IndicatorVisibility(ManagedObjectVisibility, TestCase):
    def setUp(self):
        super(IndicatorVisibility, self).setUp()
        self.item = models.Indicator.objects.create(
            name="Test Indicator",
            workgroup=self.wg,
        )


class IndicatorAdmin(AdminPageForConcept, TestCase):
    itemType = models.Indicator


class IndicatorViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.Indicator

    @tag('perms')
    def test_component_permsission_checks(self):
        viewable = MDR.DataElement.objects.create(
            name='viewable data element', definition='Viewable', submitter=self.editor
        )
        invis = MDR.DataElement.objects.create(
            name='invisible data element', definition='Invisible'
        )
        self.item1.add_numerator(data_element=viewable)
        self.item1.add_numerator(data_element=viewable)
        self.item1.add_denominator(data_element=invis)

        self.login_editor()
        response = self.client.get(
            self.item1.get_absolute_url()
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(viewable.id in response.context['viewable_ids'])
        self.assertTemplateUsed(response, 'comet/indicator.html')

        self.assertContains(response, viewable.name)
        self.assertNotContains(response, invis.name)
        self.assertContains(response, 'You don\'t have permission', count=1)

    def test_weak_editing_in_advanced_editor_dynamic(self, updating_field=None, default_fields={}):
        de = MDR.DataElement.objects.create(
            name="test name",
            definition="test definition",
        )
        de.save()

        for i in range(4):
            self.item1.add_numerator(data_element=de)

        for i in range(3):
            self.item1.add_denominator(data_element=de)

        for i in range(2):
            self.item1.add_disaggregator(data_element=de)

        default_fields = {
            'data_element': de.id,
        }

        super().test_weak_editing_in_advanced_editor_dynamic(updating_field='description',
                                                             default_fields=default_fields)


class IndicatorSetViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.IndicatorSet

    def test_weak_editing_in_advanced_editor_dynamic(self, updating_field=None, default_fields={}):
        """Test editing of indicator inclusions

        overrides general weak editor test
        """
        self.login_editor()

        # Create models
        indicator = models.Indicator.objects.create(
            name='Indicator of goodness',
            definition='Indicator of goodness',
        )

        inclusions = []
        for i in range(4):
            inc = models.IndicatorInclusion.objects.create(
                order=i,
                indicator_set=self.item1,
                indicator=indicator,
                name='Some indicator',
            )
            inclusions.append(inc)

        # Serialize item
        data = model_to_dict_with_change_time(self.item1)

        # Serialize inclusions, make edit to name
        incdata = self.bulk_serialize_inclusions(inclusions, ['indicator_set'])
        for item in incdata:
            item['name'] = 'The best indicator'
        data.update(self.get_formset_postdata(incdata, 'indicators', 4))

        # Post edit
        response = self.client.post(
            reverse('aristotle:edit_item', args=[self.item1.id]),
            data
        )
        self.assertEqual(response.status_code, 302)

        # Check result
        self.assertEqual(self.item1.indicatorinclusion_set.count(), 4)
        for inc in self.item1.indicatorinclusion_set.all():
            # Check old values
            self.assertEqual(inc.indicator, indicator)
            # Check new values
            self.assertEqual(inc.name, 'The best indicator')


class QualityStatementViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.QualityStatement


class OutcomeAreaViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.OutcomeArea


class FrameworkViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.Framework

    def test_weak_editing_in_advanced_editor_dynamic(self, updating_field=None, default_fields={}):
        """Test editing of framework dimensions

        overrides general weak editor test
        """
        self.login_editor()

        dimensions = []
        for i in range(4):
            dim = models.FrameworkDimension.objects.create(
                framework=self.item1,
                name='Dimension',
                description='An average dimension'
            )
            dimensions.append(dim)

        # Serialize item
        data = model_to_dict_with_change_time(self.item1)

        dimension_data = self.bulk_serialize_inclusions(dimensions, ['framework'], '')
        for item in dimension_data:
            item['description'] = 'An amazing dimension'
        data.update(self.get_formset_postdata(dimension_data, 'dimensions', 4))

        # Post edit
        response = self.client.post(
            reverse('aristotle:edit_item', args=[self.item1.id]),
            data
        )
        self.assertEqual(response.status_code, 302)

        # Check that changes have been applied
        self.assertEqual(self.item1.frameworkdimension_set.count(), 4)
        for fd in self.item1.frameworkdimension_set.all():
            self.assertEqual(fd.name, 'Dimension')
            self.assertEqual(fd.description, 'An amazing dimension')
