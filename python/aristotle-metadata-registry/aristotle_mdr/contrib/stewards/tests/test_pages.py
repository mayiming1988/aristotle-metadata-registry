from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from aristotle_mdr import models as mdr_models
from aristotle_mdr import perms
from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.tests import utils
from aristotle_mdr.contrib.stewards.tests.test_perms import BaseStewardOrgsTestCase

User = get_user_model()


class OrgPagesTests(BaseStewardOrgsTestCase, TestCase):
    def setUp(self):
        super().setUp()

        self.item = mdr_models.ObjectClass.objects.create(
            name='Org 1',
            definition="1",
            stewardship_organisation=self.steward_org_1,
            workgroup=self.wg1
        )

        self.assertIn(
            self.item,
            mdr_models.ObjectClass.objects.visible(self.viewer),
        )

        self.ra.register(self.item, self.ra.public_state, self.su)

    def test_member_search(self):
        self.login_superuser()

        self.assertTrue(self.org_manager.stewardorganisationmembership_set.count() == 1)
        self.assertTrue(self.org_member_2.stewardorganisationmembership_set.count() == 1)

        org_manager_role = self.org_manager.stewardorganisationmembership_set.first()
        org_member_role = self.org_member_2.stewardorganisationmembership_set.first()

        member_search_url = reverse(
            "aristotle_mdr:stewards:group:member_list", args=[self.steward_org_1.slug]
        ) + "?user_filter={user}&role={role}"
        response = self.client.get(member_search_url.format(user="",role=""))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertTrue(org_member_role in response.context['object_list'])

        member_search_url = reverse(
            "aristotle_mdr:stewards:group:member_list", args=[self.steward_org_1.slug]
        ) + "?user_filter={user}&role_filter={role}"
        response = self.client.get(member_search_url.format(user="oscar",role=""))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertFalse(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="frank",role=""))
        self.assertFalse(org_manager_role in response.context['object_list'])
        self.assertTrue(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="",role=""))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertTrue(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="",role="admin"))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertFalse(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="frankie",role="admin"))
        self.assertFalse(org_manager_role in response.context['object_list'])
        self.assertFalse(org_member_role in response.context['object_list'])
