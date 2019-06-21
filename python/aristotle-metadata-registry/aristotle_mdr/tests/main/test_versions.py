import aristotle_mdr.models as MDR
import aristotle_dse.models as DSE
from aristotle_mdr.tests import utils
from aristotle_mdr.contrib.publishing.models import VersionPermissions
from aristotle_mdr.constants import visibility_permission_choices as VISIBILITY_PERMISSION_CHOICES

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.test import override_settings
from django.conf import settings
import reversion
from reversion.models import Version


class VersionComparisionTestCase(utils.AristotleTestUtils, TestCase):
    """Class to test the version comparision view"""

    def setUp(self):
        super().setUp()

        self.object_class = MDR.ObjectClass.objects.create(
            name='Object Class',
            definition='description',
            submitter=self.editor,
            workgroup=self.wg1,
        )

        self.data_element = MDR.DataElement.objects.create(
            name="Data Element",
            definition="definition",
            submitter=self.editor,
            workgroup=self.wg1
        )

        aristotle_settings = settings.ARISTOTLE_SETTINGS
        aristotle_settings['CONTENT_EXTENSIONS'].append('aristotle_dse')
        with override_settings(ARISTOTLE_SETTINGS=aristotle_settings):
            self.data_set_specification = DSE.DataSetSpecification.objects.create(
                name='Data Set Specification',
                definition='definition',
                submitter=self.editor,
                workgroup=self.wg1
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

    def test_version_compare_chronology_correct(self):
        """Test that the versions are compared with the correct chronology. We want the earlier item to be version 1
        and the older item to be version 2"""

        # Create two versions of an Object Class
        with reversion.revisions.create_revision():
            self.object_class.name = "Older Version of a Person"
            self.object_class.save()

        with reversion.revisions.create_revision():
            self.object_class.name = "Newer Version of a Person"
            self.object_class.save()

        # Confirm that two versions were created
        versions = reversion.models.Version.objects.get_for_object(self.object_class)
        self.assertEqual(versions.count(), 2)

        # Build query in the wrong order
        url = reverse('aristotle:compare', args=[self.object_class])
        query_url = url + '?v1={}&v2={}'.format()
        # Assert that they have been correctly rearranged


    def test_html_fields_of_custom_values_detected_as_html_fields(self):
        """Test that the HTML fields of custom values are correctly detected as HTML fields. A test is written
        for this because CustomFields store HTML fields as TextFields so we have custom logic to deal with that"""


    def test_view_rendered_html_field_for_subitem(self):
        """Test that the CompareFieldsHTMLView renders the value of a subitem's HTML field. Using the definition
         of a DSS Grouping as a indicative value"""

        self.login_viewer()
        # Create two versions with DSSGroupings
        with reversion.revisions.create_revision():
            dss_grouping = DSE.DSSGrouping.objects.create(
                dss=self.data_set_specification,
                name='Grouping',
                definition='This is a DSS Grouping')

            self.data_set_specification.save()

        with reversion.revisions.create_revision():
            dss_grouping.definition = 'This is an updated DSS Grouping'
            dss_grouping.save()
            self.data_set_specification.save()

        # Confirm that two versions were created
        versions = reversion.models.Version.objects.get_for_object(self.data_set_specification)
        self.assertEqual(versions.count(), 2)

        # Build the get query parameter. Format is parent_field.{{ number of subitem indexed from 0}}.field
        url = reverse('aristotle:compare_fields', args=[self.data_set_specification.id])
        query = url + '?v1={}&v2={}&field=groups.0.definition'.format(versions[0].id, versions[1].id)

        response = self.client.get(query)
        self.assertEqual(response.status_code, 200)

        # Check the content of the fields
        self.assertEqual(response.context['html_fields'], ['This is an updated DSS Grouping', 'This is a DSS Grouping'])


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
            self.reversion_item_without_permissions = MDR.ObjectClass.objects.create(
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
            self.reversion_item_with_workgroup_permission = MDR.ObjectClass.objects.create(
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
            self.reversion_item_with_authenticated_user_permissions = MDR.ObjectClass.objects.create(
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
            self.reversion_item_with_public_permissions = MDR.ObjectClass.objects.create(
                name='A item for authenticated users only',
                definition="Authenticated user permission",
                submitter=self.editor,
                workgroup=self.wg1)

        self.version_with_public_user_permission = Version.objects.get_for_object(
            self.reversion_item_with_public_permissions).first()

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
            item_without_permissions = MDR.ObjectClass.objects.create(
                name="A concept without permissions",
                definition="Concept with no permissions",
                submitter=self.editor,
                workgroup=self.wg1
            )
            reversion.revisions.set_comment("First edit")

        self.so = MDR.StewardOrganisation.objects.create(
            name='Best Stewardship Organisation',
        )

        self.ra = MDR.RegistrationAuthority.objects.create(
            name='First RA',
            definition='First',
            stewardship_organisation=self.so
        )
        # Register the ObjectClass as public, but not the version
        self.status = MDR.Status.objects.create(
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
            self.sandbox_item = MDR.ObjectClass.objects.create(
                name="A published item",
                definition="Concept with no permissions",
                submitter=self.regular)

        response = self.client.get(reverse('aristotle:item_history', args=[self.sandbox_item.id]))
        self.assertEqual((len(response.context['versions'])), 1 )


class CreationOfVersionTests(utils.AristotleTestUtils, TestCase):
    def test_newly_created_version_permissions_default_to_workgroup(self):
        # ///Arrange
        self.login_editor()

        object_class = MDR.ObjectClass.objects.create(
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
        object_class = MDR.ObjectClass.objects.get(pk=object_class.pk)

        #///Assert

        self.assertEqual(object_class.name, updated_name)

        # Load the version
        version = Version.objects.get_for_object(
            object_class).first()

        # Load the associated VersionPermission object
        version_permission = VersionPermissions.objects.get_object_or_none(version=version)

        # Check that it defaults to 2
        self.assertEqual(version_permission.visibility, VISIBILITY_PERMISSION_CHOICES.workgroup)








