from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, tag

from aristotle_mdr import models as mdr_models
from aristotle_mdr import perms
from aristotle_mdr.models import StewardOrganisation, Workgroup
from aristotle_mdr.tests import utils
from aristotle_mdr.tests.main.test_bulk_actions import BulkActionsTest
from aristotle_mdr.utils import setup_aristotle_test_environment
from aristotle_mdr.contrib.slots.utils import concepts_with_similar_slots

import datetime
import json

User = get_user_model()
setup_aristotle_test_environment()


class BaseStewardOrgsTestCase(utils.AristotleTestUtils):
    def setUp(self):
        super().setUp()

        self.steward_org_1 = StewardOrganisation.objects.create(
            name='Org 1',
            description="1",
        )

        self.steward_org_2 = StewardOrganisation.objects.create(
            name='Org 1',
            description="2",
        )

        self.org_manager = User.objects.create(
            email="oscar@aristotle.example.com",
            short_name="Oscar"
        )
        self.steward_org_1.grant_role(
            role=StewardOrganisation.roles.admin,
            user=self.org_manager,
        )

class OrgPermissionsTests(BaseStewardOrgsTestCase, TestCase):
    def test_user_is_owner(self):
        self.assertTrue(self.steward_org_1.is_owner(self.org_manager))
        self.assertFalse(self.steward_org_2.is_owner(self.org_manager))

        self.steward_org_2.grant_role(
            role=StewardOrganisation.roles.admin,
            user=self.org_manager,
        )
        self.assertTrue(self.steward_org_2.is_owner(self.org_manager))

    def test_org_admin_can_create_workgroup(self):
        self.assertTrue(perms.user_can_create_workgroup(
            self.org_manager, self.steward_org_1,
        ))
        self.assertFalse(perms.user_can_create_workgroup(
            self.org_manager, self.steward_org_2,
        ))
        self.steward_org_2.grant_role(
            role=StewardOrganisation.roles.admin,
            user=self.org_manager,
        )
        self.assertTrue(perms.user_can_create_workgroup(
            self.org_manager, self.steward_org_2,
        ))
        self.steward_org_2.state = StewardOrganisation.states.archived
        self.steward_org_2.save()

        self.assertFalse(perms.user_can_create_workgroup(
            self.org_manager, self.steward_org_2,
        ))

    def test_org_admin_can_manage_workgroup(self):
        wg = mdr_models.Workgroup.objects.create(
            name="Test", definition="",
            stewardship_organisation=self.steward_org_1    
        )
        
        self.assertTrue(perms.user_can_manage_workgroup(self.org_manager, wg))

        self.assertTrue(self.steward_org_1.is_active())
        self.steward_org_1.state = StewardOrganisation.states.archived
        self.steward_org_1.save()
        self.assertFalse(self.steward_org_1.is_active())

        self.assertFalse(perms.user_can_manage_workgroup(self.org_manager, wg))

    def test_org_admin_can_create_registration_authority(self):
        self.assertTrue(perms.user_can_create_registration_authority(
            self.org_manager, self.steward_org_1,
        ))
        self.assertFalse(perms.user_can_create_registration_authority(
            self.org_manager, self.steward_org_2,
        ))
        obj_id = self.steward_org_2.grant_role(
            role=StewardOrganisation.roles.admin,
            user=self.org_manager,
        )
        # logger.critical()
        self.assertTrue(perms.user_can_create_registration_authority(
            self.org_manager, self.steward_org_2,
        ))
        
        self.steward_org_2.state = StewardOrganisation.states.archived
        self.steward_org_2.save()

        self.assertFalse(perms.user_can_create_registration_authority(
            self.org_manager, self.steward_org_2,
        ))
