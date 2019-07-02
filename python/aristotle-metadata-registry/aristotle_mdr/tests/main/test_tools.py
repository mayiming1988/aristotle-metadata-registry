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

        self.status_oc_non_standard = models.Status.objects.create(
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

        self.status_dec_non_standard = models.Status.objects.create(
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

        self.status_vd_non_standard = models.Status.objects.create(
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

        self.status_de_standard = models.Status.objects.create(
            concept=self.de_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.standard,
        )

        # self.logout()

    def test_it_works(self):

        standard_status = '5'

        ra_id = str(self.ra.id)

        # Data Element query
        response = self.client.get(
            reverse(
                'aristotle:reportingTool') + '?registration_authorities_select=' + ra_id + '&data_types_select=0&statuses_select=' + standard_status
        )

        # qs = response.context['data_elements']

        import pdb
        pdb.set_trace()

        # self.assertEqual(qs.count(), 1)

        import pdb
        pdb.set_trace()