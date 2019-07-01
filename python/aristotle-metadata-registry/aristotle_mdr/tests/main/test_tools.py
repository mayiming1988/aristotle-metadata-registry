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

        # Create a ValueDomain.
        self.vd_std = models.ValueDomain.objects.create(
            name="My Value Domain",
            definition="My vd...",
            workgroup=self.wg1,
        )

        # Create a DataElement "connected" to the previous ValueDomain.
        self.de_std = models.DataElement.objects.create(
            name="My Data Element",
            definition="My data elem...",
            workgroup=self.wg1,
            valueDomain=self.vd_std,
        )

        # Create a "Standard" Status object for the RA and DataElement.
        self.status_de_standard = models.Status.objects.create(
            concept=self.de_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.standard,
        )

        # Create a "Standard" Status object for the RA and ValueDomain.
        self.status_vd_std = models.Status.objects.create(
            concept=self.vd_std,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=models.STATES.standard,
        )

        standard_status = '5'

        ra_id = str(self.ra.id)

        # Data Element query
        response = self.client.get(
            reverse('aristotle:reportingTool') + '?registration_authorities_select' + ra_id + '&data_types_select=0&statuses_select=' + standard_status
        )

        object = models.Status.objects.current().filter(registrationAuthority=self.ra, state=standard_status)

        empty_queryset = models.Status.objects.current().filter(registrationAuthority=self.ra).exclude(state=standard_status)

        import pdb
        pdb.set_trace()

        self.logout()
