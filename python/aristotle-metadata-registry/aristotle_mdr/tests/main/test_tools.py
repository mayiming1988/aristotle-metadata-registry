from django.utils import timezone

from django.test import TestCase
from django.urls import reverse

from django.shortcuts import redirect
from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models


class AristotleReportingToolsPage(AristotleTestUtils, TestCase):
    url_name = 'reportingTool'

    def setUp(self):
        super().setUp()

        self.login_superuser()

        self.property_non_std = models.Property.objects.create(
            name="My PROPERTY NON STANDARD",
            definition="My prop",
            workgroup=self.wg1,
        )

        self.status_prop_non_standard = models.Status.objects.create(
            concept=self.property_non_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.qualified,
        )

        self.object_class_non_std = models.Property.objects.create(
            name="My OBJECT CLASS NON STANDARD",
            definition="My oc...",
            workgroup=self.wg1,
        )

        models.Status.objects.create(
            concept=self.object_class_non_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.qualified,
        )

        self.dec_non_std = models.DataElementConcept.objects.create(
            name="My DEC",
            definition="MY dec...",
            workgroup=self.wg1,
            property=self.property_non_std
        )

        models.Status.objects.create(
            concept=self.property_non_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.qualified,
        )

        self.vd_non_std = models.ValueDomain.objects.create(
            name="My Value Domain",
            definition="My vd...",
            workgroup=self.wg1,
        )

        models.Status.objects.create(
            concept=self.vd_non_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.qualified,
        )

        self.de_std = models.DataElement.objects.create(
            name="My Data Element",
            definition="My data elem...",
            workgroup=self.wg1,
            valueDomain=self.vd_non_std,
        )

        models.Status.objects.create(
            concept=self.de_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.standard,
        )

        self.logout()

    def test_there_is_only_one_standard_data_element(self):

        standard_status = '5'

        response = self.client.get(
            reverse(
                'aristotle:reportingTool') + '?ra=' + str(self.ra.id) + '&status=' + standard_status
        )

        self.assertEqual(response.context['object_list'].count(), 1)

    def test_query_only_returns_data_elements_with_components(self):

        incomplete_status = '1'

        my_data_element = models.DataElement.objects.create(
            name="My lonely data element",
            definition="I am so lonely. I have no subcomponents.",
            workgroup=self.wg1,
        )

        my_status_for_lonely_data_element = models.Status.objects.create(
            concept=my_data_element,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.incomplete,
        )

        response = self.client.get(
            reverse(
                'aristotle:reportingTool') + '?ra=' + str(self.ra.id) + '&status=' + incomplete_status
        )

        self.assertEqual(response.context['object_list'].count(), 0)

    def test_query_only_fetches_data_elements_with_components_with_different_statuses(self):

        qualified_status = '4'

        data_element_concept_for_de_qualified = models.DataElementConcept.objects.create(
            name="MY DEC for DE Qualified.",
            definition="mY DEC",
            workgroup=self.wg1,
        )

        de_qualified = models.DataElement.objects.create(
            name="My Qualified Data Element",
            definition="My non standard data elem...",
            workgroup=self.wg1,
            dataElementConcept=data_element_concept_for_de_qualified,
        )

        # Same Status!
        models.Status.objects.create(
            concept=de_qualified,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.qualified,
        )

        # Same Status!
        models.Status.objects.create(
            concept=data_element_concept_for_de_qualified,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.qualified,
        )

        response = self.client.get(
            reverse(
                'aristotle:reportingTool') + '?ra=' + str(self.ra.id) + '&status=' + qualified_status
        )

        self.assertEqual(response.context['object_list'].count(), 0)

    def test_data_elements_fetched_correspond_to_the_right_ra(self):

        prefered_status = '6'

        another_ra = models.RegistrationAuthority.objects.create(
            name="Me second RA",
            definition="My second RA",
            stewardship_organisation=self.steward_org_1,
        )

        vd_for_data_element_with_second_ra = models.ValueDomain.objects.create(
            name="VD for data element with second ra",
            definition="My VD",
            workgroup=self.wg1,
        )

        data_element_with_second_ra = models.DataElement.objects.create(
            name="Data Element with another RA",
            definition="Data Element with another RA",
            workgroup=self.wg1,
            valueDomain=vd_for_data_element_with_second_ra
        )

        models.Status.objects.create(
            concept=data_element_with_second_ra,
            registrationAuthority=another_ra,
            registrationDate=timezone.now(),
            state=models.STATES.preferred,
        )

        response = self.client.get(
            reverse(
                'aristotle:reportingTool') + '?ra=' + str(another_ra.id) + '&status=' + prefered_status
        )

        self.assertEqual(response.context['object_list'].count(), 1)
