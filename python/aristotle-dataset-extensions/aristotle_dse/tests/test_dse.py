from unittest import skip
import reversion

import aristotle_mdr.models as MDR
from aristotle_dse import models
from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.main.test_wizards import ConceptWizardPage
from aristotle_mdr.tests.utils import ManagedObjectVisibility, model_to_dict_with_change_time
from aristotle_mdr.utils import url_slugify_concept

from django.urls import reverse
from django.test import TestCase, tag
from django.utils import timezone


def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0)


class DataSetSpecificationVisibility(ManagedObjectVisibility, TestCase):
    def setUp(self):
        super(DataSetSpecificationVisibility, self).setUp()
        self.item = models.DataSetSpecification.objects.create(name="Test DSS",
                                                               workgroup=self.wg, )


class DataSetSpecificationAdmin(AdminPageForConcept, TestCase):
    itemType = models.DataSetSpecification
    form_defaults = {
        'dssdeinclusion_set-TOTAL_FORMS': 0,
        'dssdeinclusion_set-INITIAL_FORMS': 0,
        'dsscdeinclusion_set-MAX_NUM_FORMS': 1,
        'dssclusterinclusion_set-TOTAL_FORMS': 0,
        'dssclusterinclusion_set-INITIAL_FORMS': 0,
        'dssclusterinclusion_set-MAX_NUM_FORMS': 1,
    }


class DataSetSpecificationViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.DataSetSpecification

    # TODO: Add test for dss groupings

    def test_weak_editing_in_advanced_editor_dynamic(self, updating_field=None, default_fields={}):
        """Test editing of dss inclusions, through edit page formsets

        overrides general weak editor test
        """
        self.login_editor()
        # Setup objects
        de = MDR.DataElement.objects.create(
            name="test name",
            definition="test definition",
        )
        de.save()

        inclusions = []
        clusters = []

        for i in range(4):
            inc = models.DSSDEInclusion.objects.create(
                data_element=de,
                specific_information="test info",
                conditional_inclusion="test obligation",
                order=i,
                dss=self.item1
            )
            inclusions.append(inc)

            clust = models.DSSClusterInclusion.objects.create(
                specific_information="test info",
                conditional_inclusion="test obligation",
                order=i,
                dss=self.item1,
                child=self.item1
            )
            clusters.append(clust)

        # Serialize objects
        data = model_to_dict_with_change_time(self.item1)

        # Add modified inclusion data
        incdata = self.bulk_serialize_inclusions(inclusions, ['dss'])
        for item in incdata:
            item['specific_information'] = 'dssde specific'

        data.update(self.get_formset_postdata(incdata, 'data_elements', 4))

        # Add cluster data
        clustdata = self.bulk_serialize_inclusions(clusters, ['dss'])
        for item in clustdata:
            item['specific_information'] = 'cluster specific'

        data.update(self.get_formset_postdata(clustdata, 'clusters', 4))

        # Make changes
        response = self.client.post(
            reverse('aristotle:edit_item', args=[self.item1.id]),
            data
        )
        self.assertEqual(response.status_code, 302)

        # Check updates
        self.assertEqual(self.item1.dssdeinclusion_set.count(), 4)
        for inc in self.item1.dssdeinclusion_set.all():
            # Check old values
            self.assertEqual(inc.data_element, de)
            self.assertEqual(inc.conditional_inclusion, 'test obligation')
            # Check new values
            self.assertEqual(inc.specific_information, 'dssde specific')

        self.assertEqual(self.item1.dssclusterinclusion_set.count(), 4)
        for inc in self.item1.dssclusterinclusion_set.all():
            # Check old values
            self.assertEqual(inc.child, self.item1)
            self.assertEqual(inc.conditional_inclusion, 'test obligation')
            # Check new values
            self.assertEqual(inc.specific_information, 'cluster specific')


    def test_add_data_element(self):
        de, created = MDR.DataElement.objects.get_or_create(name="Person-sex, Code N",
                                                            workgroup=self.wg1,
                                                            definition="The sex of the person with a code.",
                                                            )
        self.item1.addDataElement(de)
        self.assertTrue(self.item1.data_elements.count(), 1)

    def test_cascade_action(self):
        self.logout()
        check_url = reverse('aristotle:check_cascaded_states', args=[self.item1.pk])
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(check_url)
        self.assertTrue(response.status_code, 403)

        self.login_editor()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, check_url)  # no child items, nothing to review

        response = self.client.get(check_url)
        self.assertTrue(response.status_code, 403)

        self.test_add_data_element()  # add a data element

        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, check_url)  # now there are child items, we can review

        response = self.client.get(check_url)
        self.assertTrue(response.status_code, 200)

    def test_cloning_with_components(self):
        """Test that when an item is cloned, the included components come across"""

        # Create a Data Set Specification
        data_set_specification = models.DataSetSpecification.objects.create(
            name="Data Set Specification",
            definition="This is a data set specification"
        )
        # Create two Data Elements
        de1 = MDR.DataElement.objects.create(
            name='de1',
            definition='de1'
        )
        de2 = MDR.DataElement.objects.create(
            name='de2',
            definition='de2'
        )
        # Add data elements to a DSS
        data_set_specification.addDataElement(de1)
        data_set_specification.addDataElement(de2)

        # Login a superuser
        self.login_superuser()

        # Go to the clone item page
        response = self.client.get(reverse('aristotle:clone_item', args=[data_set_specification.id]))
        self.assertEqual(response.status_code, 200)

        # Update the cloned item's data
        data = self.get_updated_data_for_clone(response)

        # Post the cloned items data to the clone item view
        response = self.client.post(
            reverse('aristotle:clone_item', args=[data_set_specification.id]),
            data, follow=True)

        clone = response.context[-1]['object'].item  # Get the item back to check

        # Assert that the components have come across in the clone
        self.assertEqual(clone.dssdeinclusion_set.count(), 2)

    @tag('perms')
    def test_component_permission_checks(self):
        viewable = MDR.DataElement.objects.create(
            name='viewable data element', definition='Viewable', submitter=self.editor
        )
        invis = MDR.DataElement.objects.create(
            name='invisible data element', definition='Invisible'
        )
        self.item1.addDataElement(viewable)
        self.item1.addDataElement(invis)

        self.login_editor()
        response = self.client.get(
            self.item1.get_absolute_url()
        )
        self.assertTrue(viewable.id in response.context['viewable_ids'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, viewable.name)
        self.assertNotContains(response, invis.name)
        self.assertContains(response, 'You don\'t have permission', count=1)


class DataCatalogViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.DataCatalog


class DatasetViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.Dataset

    def create_public_dataset(self) -> models.Dataset:
        """Helper method that creates a public dataset"""
        dataset = models.Dataset.objects.create(name="Dataset",
                                                definition="A dataset",
                                                submitter=self.editor)
        MDR.Status.objects.create(
            concept=dataset,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=MDR.STATES.standard
        )
        return dataset


class DistributionViewPage(LoggedInViewConceptPages, TestCase):
    itemType = models.Distribution

    def test_weak_editing_in_advanced_editor_dynamic(self, updating_field=None, default_fields={}):
        de = MDR.DataElement.objects.create(
            name="test name",
            definition="test definition",
        )
        oc = MDR.ObjectClass.objects.create(
            name="a very nice object class"
        )
        oc.save()

        for i in range(4):
            models.DistributionDataElementPath.objects.create(
                data_element=de,
                logical_path=str(i),
                order=i,
                distribution=self.item1,
            )

        default_fields = {
            'specialisation_classes': oc.id,
            'data_element': de.id
        }

        super().test_weak_editing_in_advanced_editor_dynamic(updating_field='logical_path',
                                                             default_fields=default_fields)

    @skip("Rewrite of versioning, skipping for now")
    def test_version_display_many_to_many(self):
        de = MDR.DataElement.objects.create(
            name="test name",
            definition="test definition",
            workgroup=self.wg1
        )
        oc1 = MDR.ObjectClass.objects.create(
            name='oc1',
            definition='oc1',
            workgroup=self.wg1
        )
        oc2 = MDR.ObjectClass.objects.create(
            name='oc2',
            definition='oc2',
            workgroup=self.wg1
        )
        ddep = models.DistributionDataElementPath.objects.create(
            data_element=de,
            logical_path='/',
            order=0,
            distribution=self.item1
        )
        ddep.specialisation_classes.add(oc1)
        ddep.specialisation_classes.add(oc2)

        with reversion.create_revision():
            self.item1.save()

        latest = reversion.models.Version.objects.get_for_object(self.item1).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        weak = response.context['item']['weak']

        self.assertEqual(weak[0]['model'], 'Distribution Data Element Path')
        spec_classes = weak[0]['items'][0]['Specialisation Classes']

        self.assertTrue(spec_classes.is_link)
        self.assertTrue(spec_classes.is_list)
        self.assertTrue(oc1._concept_ptr in spec_classes.object_list)
        self.assertTrue(oc2._concept_ptr in spec_classes.object_list)
        self.assertEqual(len(spec_classes.object_list), 2)


class DistributionWizardPage(ConceptWizardPage, TestCase):
    model = models.Distribution

    def do_test_for_issue333(self, response):
        self.assertTrue(self.extra_wg in response.context['form'].fields['workgroup'].queryset)

    @tag('edit_formsets')
    def test_weak_editor_during_create(self):
        self.de1 = MDR.DataElement.objects.create(name='DE1 - visible', definition="my definition", workgroup=self.wg1)
        self.de2 = MDR.DataElement.objects.create(name='DE2 - visible', definition="my definition", workgroup=self.wg1)
        self.de3 = MDR.DataElement.objects.create(name='DE3 - visible', definition="my definition", workgroup=self.wg1)

        self.oc1 = MDR.ObjectClass.objects.create(name='OC1 - visible', definition="my definition", workgroup=self.wg1)
        self.oc2 = MDR.ObjectClass.objects.create(name='OC2 - visible', definition="my definition", workgroup=self.wg1)
        self.oc3 = MDR.ObjectClass.objects.create(name='OC3 - visible', definition="my definition", workgroup=self.wg1)

        self.login_editor()

        item_name = 'My Fancy New Distribution'
        step_1_data = {
            self.wizard_form_name + '-current_step': 'initial',
            'initial-name': item_name,
        }

        response = self.client.post(self.wizard_url, step_1_data)
        wizard = response.context['wizard']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard['steps'].current, 'results')

        step_2_data = {
            self.wizard_form_name + '-current_step': 'results',
            'initial-name': item_name,
            'results-name': item_name,
            'results-definition': "Test Definition",
        }
        step_2_data.update(self.get_formset_postdata([], 'slots'))
        step_2_data.update(self.get_formset_postdata([], 'org_records'))

        ddep_formset_data = [
            {'data_element': self.de1.pk, 'logical_path': '/garbage/file',
             'specialisation_classes': [self.oc1.pk, self.oc3.pk], 'ORDER': 0},
            {'data_element': self.de3.pk, 'logical_path': '/garbage/file',
             'specialisation_classes': [self.oc2.pk, self.oc3.pk], 'ORDER': 1},
        ]
        step_2_data.update(self.get_formset_postdata(ddep_formset_data, 'data_elements'))

        response = self.client.post(self.wizard_url, step_2_data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.model.objects.filter(name=item_name).exists())
        self.assertEqual(self.model.objects.filter(name=item_name).count(), 1)
        item = self.model.objects.filter(name=item_name).first()
        self.assertRedirects(response, url_slugify_concept(item))

        ddeps = item.distributiondataelementpath_set.all().order_by('order')

        self.assertEqual(ddeps[0].order, 0)
        self.assertEqual(ddeps[0].data_element, self.de1)
        self.assertEqual(ddeps[0].logical_path, '/garbage/file')
        self.assertEqual(ddeps[0].specialisation_classes.count(), 2)
        self.assertTrue(self.oc1 in ddeps[0].specialisation_classes.all())
        self.assertTrue(self.oc3 in ddeps[0].specialisation_classes.all())

        self.assertEqual(ddeps[1].order, 1)
        self.assertEqual(ddeps[1].data_element, self.de3)
        self.assertEqual(ddeps[1].logical_path, '/garbage/file')
        self.assertEqual(ddeps[1].specialisation_classes.count(), 2)
        self.assertTrue(self.oc2 in ddeps[1].specialisation_classes.all())
        self.assertTrue(self.oc3 in ddeps[1].specialisation_classes.all())
