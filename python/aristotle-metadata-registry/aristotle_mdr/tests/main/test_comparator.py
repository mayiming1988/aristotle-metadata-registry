import aristotle_mdr.models as MDR
import aristotle_dse.models as DSE
import aristotle_mdr.tests.utils as utils

from django.test import TestCase
from django.urls import reverse


class ComparatorTester(utils.LoggedInViewPages, TestCase):
    def setUp(self):
        super().setUp()
        self.steward_org_1 = MDR.StewardOrganisation.objects.create(name="Test SO")
        self.ra = MDR.RegistrationAuthority.objects.create(name="Test RA", stewardship_organisation=self.steward_org_1)
        self.wg = MDR.Workgroup.objects.create(name="Setup WG", stewardship_organisation=self.steward_org_1)

    def test_compare_with_no_selections_shows_please_select_item_prompt(self):
        """Test that when the compare page has no selections a prompt is given"""
        self.login_superuser() # We don't need to worry about permissions here
        response = self.client.get(reverse('aristotle:compare_concepts'))
        self.assertResponseStatusCodeEqual(response=response, code=200)
        self.assertEqual(response.context['not_all_versions_selected'], True)

    def test_user_can_compare_different_dss_objects(self):
        """Test that when a user compares two different data elements within a DSS the difference is displayed"""
        # Create two different Data Elements
        self.login_superuser() # We're not worried about permissions in this test

        data_element_1 = MDR.DataElement.objects.create(name="Data Element 1",
                                                        definition="My first Data Element",
                                                        submitter=self.editor,
                                                        )
        data_element_2 = MDR.DataElement.objects.create(name="Data Element 2",
                                                        definition="My second Data Element",
                                                        submitter=self.editor)
        data_set_specification_1 = DSE.DataSetSpecification.objects.create(name="Data Set Specification 1",
                                                                           definition='',
                                                                           submitter=self.editor)
        data_set_specification_2 = DSE.DataSetSpecification.objects.create(name='Data Set Specification 2',
                                                                           definition='',
                                                                           submitter=self.editor)

        DSE.DSSDEInclusion.objects.create(dss=data_set_specification_1, data_element=data_element_1)
        DSE.DSSDEInclusion.objects.create(dss=data_set_specification_2, data_element=data_element_2)

        response = self.client.get(reverse('aristotle:compare_concepts')
                                   + f'?item_a={data_set_specification_1.pk}&item_b={data_set_specification_2.pk}')
        self.assertResponseStatusCodeEqual(response=response, code=200)
        self.assertContainsHtml(response, 'first')
        self.assertContainsHtml(response, 'second')

    def test_user_can_compare_different_distribution_objects(self):
        pass
        # TODO: Make a test that compares two Distributions and identifies different Data Elements
