from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from aristotle_mdr import models as mdr_models
from aristotle_mdr import perms
from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.tests import utils

User = get_user_model()


class BaseStewardOrgsTestCase(utils.AristotleTestUtils):

    def setUp(self):
        super().setUp()

        self.steward_org_2 = StewardOrganisation.objects.create(
            name='Org 1',
            description="2",
            state=StewardOrganisation.states.active
        )

        self.org_manager = User.objects.create_user(
            email="oscar@aristotle.example.com",
            short_name="Oscar",
            password="naughty_cat"
        )
        self.steward_org_1.grant_role(
            role=StewardOrganisation.roles.admin,
            user=self.org_manager,
        )
        self.org_member_2 = User.objects.create_user(
            email="frankie@aristotle.example.com",
            short_name="Frankie",
            password="naughty_kitten"
        )
        self.steward_org_1.grant_role(
            role=StewardOrganisation.roles.member,
            user=self.org_member_2,
        )
        self.org_steward = User.objects.create(
            email="steve@aristotle.example.com",
            short_name="steve"
        )
        self.steward_org_1.grant_role(
            role=StewardOrganisation.roles.steward,
            user=self.org_steward,
        )
        self.org_member = User.objects.create(
            email="martin@aristotle.example.com",
            short_name="martin"
        )
        self.steward_org_1.grant_role(
            role=StewardOrganisation.roles.member,
            user=self.org_member,
        )

        self.assertTrue(
            self.steward_org_1.has_role(
                role=StewardOrganisation.roles.admin,
                user=self.org_manager,
            )
        )
        self.assertTrue(
            self.steward_org_1.has_role(
                role=StewardOrganisation.roles.steward,
                user=self.org_steward,
            )
        )
        self.assertTrue(
            self.steward_org_1.has_role(
                role=StewardOrganisation.roles.member,
                user=self.org_member,
            )
        )

    def login_oscar(self):
        success = self.client.login(email='oscar@aristotle.example.com', password='naughty_cat')
        self.assertTrue(success)

    def login_frankie(self):
        success = self.client.login(email='frankie@aristotle.example.com', password='naughty_kitten')
        self.assertTrue(success)


class OrgGroupHasPermissions(BaseStewardOrgsTestCase, TestCase):
    def test_admin_permissions(self):
        org_1_role_permissions = {
            "view_group": True,
            "manage_workgroups": True,
            "publish_objects": True,
            "manage_regstration_authorities": True,
            "edit_group_details": True,
            "edit_members": True,
            "invite_member": True,
            "manage_managed_items": True,
            "list_workgroups": True,
            "manage_references": True,
        }
        for permission_name, is_permitted in org_1_role_permissions.items():
            self.assertEqual(
                self.steward_org_1.user_has_permission(user=self.org_manager, permission=permission_name),
                is_permitted,
                msg="User permission failed for - %s" % permission_name
            )

        for permission_name in StewardOrganisation.role_permissions.keys():
            self.assertEqual(
                self.steward_org_2.user_has_permission(user=self.org_member, permission=permission_name),
                permission_name in ['view_group'],
                msg="User permission failed for - %s" % permission_name
            )

    def test_steward_permissions(self):
        org_1_role_permissions = {
            "view_group": True,
            "manage_workgroups": False,
            "publish_objects": True,
            "manage_regstration_authorities": False,
            "edit_group_details": False,
            "edit_members": False,
            "invite_member": False,
            "manage_managed_items": True,
            "list_workgroups": True,
            "manage_references": True,
        }
        for permission_name, is_permitted in org_1_role_permissions.items():
            self.assertEqual(
                self.steward_org_1.user_has_permission(user=self.org_steward, permission=permission_name),
                is_permitted,
                msg="User permission failed for - %s" % permission_name
            )

        for permission_name in StewardOrganisation.role_permissions.keys():
            self.assertEqual(
                self.steward_org_2.user_has_permission(user=self.org_member, permission=permission_name),
                permission_name in ['view_group'],
                msg="User permission failed for - %s" % permission_name
            )

    def test_member_permissions(self):
        org_1_role_permissions = {
            "view_group": True,
            "manage_workgroups": False,
            "publish_objects": False,
            "manage_regstration_authorities": False,
            "edit_group_details": False,
            "edit_members": False,
            "invite_member": False,
            "manage_managed_items": False,
            "list_workgroups": True,
            "manage_references": False,
        }
        for permission_name, is_permitted in org_1_role_permissions.items():
            self.assertEqual(
                self.steward_org_1.user_has_permission(user=self.org_member, permission=permission_name),
                is_permitted,
                msg="User permission failed for - %s" % permission_name
            )

        for permission_name in StewardOrganisation.role_permissions.keys():
            self.assertEqual(
                self.steward_org_2.user_has_permission(user=self.org_member, permission=permission_name),
                permission_name in ['view_group'],
                msg="User permission failed for - %s" % permission_name
            )

    def test_permissions_for_hidden(self):
        self.steward_org_1.state = StewardOrganisation.states.hidden
        self.steward_org_1.save()
        self.steward_org_1.refresh_from_db()
        self.assertTrue(self.steward_org_1.state == StewardOrganisation.states.hidden)
        self.assertFalse(self.steward_org_1.is_active())

        for permission_name in StewardOrganisation.role_permissions.keys():
            self.assertEqual(
                self.steward_org_1.user_has_permission(user=self.org_manager, permission=permission_name),
                False,
                msg="User permission failed for - %s" % permission_name
            )


class OrgConceptVisibilityTests(BaseStewardOrgsTestCase, TestCase):
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

    def test_state_changes(self):
        self.assertIn(
            self.item,
            mdr_models.ObjectClass.objects.public(),
        )
        self.assertIn(
            self.item,
            mdr_models.ObjectClass.objects.visible(self.viewer),
        )

        self.steward_org_1.state = StewardOrganisation.states.hidden
        self.steward_org_1.save()
        self.item.refresh_from_db()
        self.assertEquals(
            self.item.stewardship_organisation.state,
            StewardOrganisation.states.hidden
        )

        self.assertNotIn(
            self.item,
            mdr_models.ObjectClass.objects.public(),
        )
        self.assertNotIn(
            self.item,
            mdr_models.ObjectClass.objects.visible(self.viewer),
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
        self.assertTrue(perms.user_can_create_registration_authority(
            self.org_manager, self.steward_org_2,
        ))
        
        self.steward_org_2.state = StewardOrganisation.states.archived
        self.steward_org_2.save()

        self.assertFalse(perms.user_can_create_registration_authority(
            self.org_manager, self.steward_org_2,
        ))
