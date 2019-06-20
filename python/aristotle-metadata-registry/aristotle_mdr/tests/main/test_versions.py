import aristotle_mdr.models as mdr_models
from aristotle_mdr.tests import utils
from aristotle_mdr.contrib.publishing.models import VersionPermissions
from aristotle_mdr.constants import visibility_permission_choices as VISIBILITY_PERMISSION_CHOICES

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

import reversion
from reversion.models import Version


class VersionComparisionTestCase(utils.AristotleTestUtils, TestCase):
    """Class to test the version comparision view"""

    def setUp(self):
        super().setUp()

        self.item = mdr_models.ObjectClass.objects.create(
            name='Test Item',
            definition='Test Item Description',
            submitter=self.editor,
            workgroup=self.wg1,
        )

    def test_altered_on_concept_field_displayed(self):
        """Test that field that is **on** the concept, and has
        had content altered between the saves is displayed"""

    def test_added_subitem_displayed(self):
        """Test that a subitem (ex. custom fields) added to a concept between versions is displayed """

    def test_removed_subitem_displayed(self):
        """Test that a subitem (ex. custom fields) removed from a concept between versions is displayed"""

    def test_changed_subitem_displayed(self):
        """Test that a subitem (ex. custom fields) that has had content on it altered is displayed """

    def test_version_chronology_correct(self):
        """Test that the versions are compared with the correct chronology"""


class DataElementComparisionTestCase(utils.AristotleTestUtils, TestCase):
    """Class to test the comparision of Value Domain specific fields"""
    def setUp(self):
        super().setUp()

    def test_value_domain_changes_displayed(self):
        """Test that values displayed are """
        pass


class TestViewingVersionPermissions(utils.AristotleTestUtils, TestCase):
    """ Class to test the version permissions  """
    def setUp(self):
        super().setUp()

        # Create a new item without version permissions
        with reversion.revisions.create_revision():
            self.reversion_item_without_permissions = mdr_models.ObjectClass.objects.create(
                name="A concept without permissions",
                definition="Concept with no permissions",
                submitter=self.editor,
                workgroup=self.wg1
            )
            reversion.revisions.set_comment("First edit")

        self.version_without_permission = Version.objects.get_for_object(
            self.reversion_item_without_permissions).first()

        # Item with workgroup version permissions
        with reversion.revisions.create_revision():
            self.reversion_item_with_workgroup_permission = mdr_models.ObjectClass.objects.create(
                name="A published item",
                definition="Concept with no permissions",
                submitter=self.editor,
                workgroup=self.wg1
            )

        self.version_with_workgroup_permission = Version.objects.get_for_object(
            self.reversion_item_with_workgroup_permission).first()

        VersionPermissions.objects.create(version=self.version_with_workgroup_permission,
                                          visibility=VISIBILITY_PERMISSION_CHOICES.workgroup)

        # Item with authenticated user version permissions
        with reversion.revisions.create_revision():
            self.reversion_item_with_authenticated_user_permissions = mdr_models.ObjectClass.objects.create(
                name='A item for authenticated users only',
                definition="Authenticated user permission",
                submitter=self.editor,
                workgroup=self.wg1
            )
        self.version_with_auth_user_permission = Version.objects.get_for_object(
            self.reversion_item_with_authenticated_user_permissions).first()

        VersionPermissions.objects.create(version=self.version_with_auth_user_permission,
                                          visibility=VISIBILITY_PERMISSION_CHOICES.auth)

        # Item with public version permissions
        with reversion.revisions.create_revision():
            self.reversion_item_with_public_permissions = mdr_models.ObjectClass.objects.create(
                name='A item for authenticated users only',
                definition="Authenticated user permission",
                submitter=self.editor,
                workgroup=self.wg1)

        self.version_with_public_user_permission = Version.objects.get_for_object(
            self.reversion_item_with_public_permissions
        ).first()
        VersionPermissions.objects.create(version=self.version_with_public_user_permission,
                                          visibility=VISIBILITY_PERMISSION_CHOICES.public)

    def test_superuser_can_view_version_with_no_permissions(self):
        """ Test that a superuser can view a version with no permission"""
        self.login_superuser()

        response = self.client.get(reverse('aristotle:item_history', args=[self.reversion_item_without_permissions.id]))
        self.assertEqual(len(response.context['versions']), 1)

    def test_user_in_workgroup_can_view_version_with_no_permissions(self):
        self.login_viewer()

        response = self.client.get(reverse('aristotle:item_history', args=[self.reversion_item_without_permissions.id]))
        self.assertEqual(len(response.context['versions']), 1)

    def test_user_not_in_workgroup_cant_view_version_with_no_permissions(self):
        self.login_regular_user()  # Regular user is not in workgroup

        with reversion.revisions.create_revision():
            item_without_permissions = mdr_models.ObjectClass.objects.create(
                name="A concept without permissions",
                definition="Concept with no permissions",
                submitter=self.editor,
                workgroup=self.wg1
            )
            reversion.revisions.set_comment("First edit")

        self.so = mdr_models.StewardOrganisation.objects.create(
            name='Best Stewardship Organisation',
        )

        self.ra = mdr_models.RegistrationAuthority.objects.create(
            name='First RA',
            definition='First',
            stewardship_organisation=self.so
        )
        # Register the ObjectClass as public, but not the version
        self.status = mdr_models.Status.objects.create(
            concept=item_without_permissions,
            registrationAuthority=self.ra,
            registrationDate=timezone.now(),
            state=self.ra.public_state
        )

        response = self.client.get(reverse('aristotle:item_history', args=[item_without_permissions.id]))
        self.assertEqual((len(response.context['versions'])), 0)

    def test_user_can_see_own_version_if_item_still_in_sandbox(self):
        self.login_regular_user()

        with reversion.revisions.create_revision():
            self.sandbox_item = mdr_models.ObjectClass.objects.create(
                name="A published item",
                definition="Concept with no permissions",
                submitter=self.regular)

        response = self.client.get(reverse('aristotle:item_history', args=[self.sandbox_item.id]))
        self.assertEqual((len(response.context['versions'])), 1 )


class CreationOfVersionTests(utils.AristotleTestUtils, TestCase):
    def test_newly_created_version_permissions_default_to_workgroup(self):
        # ///Arrange
        self.login_editor()

        object_class = mdr_models.ObjectClass.objects.create(
            name="A published item",
            definition="I wonder what the version permission for this is",
            submitter=self.editor
        )

        # ///Act

        # Load the EditItem page
        response = self.client.get(reverse('aristotle:edit_item', args=[object_class.id]))
        self.assertEqual(response.status_code, 200)

        # Edit the item
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        change_comment = "I changed this because I can"
        updated_item['change_comments'] = change_comment
        response = self.client.post(reverse('aristotle:edit_item', args=[object_class.id]), updated_item)

        # Decache
        object_class = mdr_models.ObjectClass.objects.get(pk=object_class.pk)

        # // Assert

        self.assertEqual(object_class.name, updated_name)

        # Load the version
        version = Version.objects.get_for_object(
            object_class).first()

        # Load the associated VersionPermission object
        version_permission = VersionPermissions.objects.get_object_or_none(version=version)

        # Check that it defaults to 2
        self.assertEqual(version_permission.visibility, VISIBILITY_PERMISSION_CHOICES.workgroup)

        # Check that the page display is 2









