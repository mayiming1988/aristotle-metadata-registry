from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from aristotle_mdr.tests.utils import AristotleTestUtils

from aristotle_mdr import models as mdr_models
from aristotle_mdr.constants import visibility_permission_choices as permission_choices
from aristotle_mdr.contrib.slots.models import Slot
from aristotle_mdr.contrib.custom_fields.models import CustomField, CustomValue
from aristotle_mdr.contrib.custom_fields.constants import CUSTOM_FIELD_STATES


class CustomFieldsTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='Very Custom Item',
            definition='Oh so custom'
        )
        self.item2 = mdr_models.ObjectClass.objects.create(
            name='Some Other Item',
            definition='Yeah Whatever'
        )

    def create_test_field(self):
        cf = CustomField.objects.create(
            order=0,
            name='Bad Word',
            type='str',
            help_text='A real bad word'
        )
        return cf

    def create_test_field_with_values(self):
        cf = self.create_test_field()
        CustomValue.objects.create(
            field=cf,
            concept=self.item.concept,
            content='Heck'
        )
        CustomValue.objects.create(
            field=cf,
            concept=self.item2.concept,
            content='Flip'
        )
        return cf

    def test_custom_fields_list(self):
        object_class_ctype = ContentType.objects.get(app_label="aristotle_mdr", model="objectclass")
        cf1 = CustomField.objects.create(
            order=0,
            name='CF1',
            type='str',
            help_text='Custom Field 1',
            allowed_model=object_class_ctype,
        )
        cf2 = CustomField.objects.create(
            order=1,
            name='CF2',
            type='str',
            help_text='Custom Field 2',
            allowed_model=object_class_ctype,
        )

        self.login_superuser()
        response = self.reverse_get(
            'aristotle_custom_fields:list',
            status_code=200,
            reverse_args=["objectclass"],
        )
        flist = response.context['list']

        self.assertEqual(flist[0]['attrs'][0], 'CF1')
        self.assertEqual(flist[1]['attrs'][0], 'CF2')

    def test_custom_field_delete(self):
        cf = self.create_test_field_with_values()
        self.assertEqual(cf.values.count(), 2)
        self.login_superuser()
        response = self.reverse_post(
            'aristotle_custom_fields:delete',
            {'method': 'delete'},
            reverse_args=[cf.id],
            status_code=302
        )
        self.assertFalse(CustomField.objects.filter(id=cf.id).exists())
        self.assertEqual(CustomValue.objects.all().count(), 0)

    def test_custom_field_migrate(self):
        cf = self.create_test_field_with_values()
        self.assertEqual(cf.values.count(), 2)
        self.login_superuser()
        response = self.reverse_post(
            'aristotle_custom_fields:delete',
            {'method': 'migrate'},
            reverse_args=[cf.id],
            status_code=302
        )
        self.assertFalse(CustomField.objects.filter(id=cf.id).exists())
        self.assertEqual(CustomValue.objects.all().count(), 0)

        slot1 = Slot.objects.get(concept=self.item.concept, name='Bad Word')
        self.assertEqual(slot1.type, 'Text')
        self.assertEqual(slot1.value, 'Heck')

        slot2 = Slot.objects.get(concept=self.item2.concept, name='Bad Word')
        self.assertEqual(slot2.type, 'Text')
        self.assertEqual(slot2.value, 'Flip')


class CustomFieldManagerTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='Person',
            definition='A Human',
            workgroup=self.wg1
        )
        self.allfield = CustomField.objects.create(
            order=0,
            name='AllField',
            type='str',
            visibility=permission_choices.public
        )
        self.authfield = CustomField.objects.create(
            order=1,
            name='AuthField',
            type='str',
            visibility=permission_choices.auth
        )
        self.wgfield = CustomField.objects.create(
            order=2,
            name='WgField',
            type='str',
            visibility=permission_choices.workgroup
        )
        self.rafield = CustomField.objects.create(
            order=3,
            name='WgField',
            type='str',
            visibility=permission_choices.administrators
        )

    def make_restricted_field(self, model):
        ct = ContentType.objects.get_for_model(model)
        restricted = CustomField.objects.create(
            order=4,
            name='Restricted',
            type='str',
            allowed_model=ct
        )
        return restricted

    def test_allowed_fields_in_wg(self):
        af = CustomField.objects.get_allowed_fields(self.item, self.editor)
        self.assertCountEqual(af, [self.authfield, self.allfield, self.wgfield])

    def test_allowed_fields_not_in_wg(self):
        af = CustomField.objects.get_allowed_fields(self.item, self.regular)
        self.assertCountEqual(af, [self.authfield, self.allfield])

    def test_allowed_fields_unath(self):
        anon = AnonymousUser()
        af = CustomField.objects.get_allowed_fields(self.item, anon)
        self.assertCountEqual(af, [self.allfield])

    def test_get_fields_for_model_for_super(self):
        rf = self.make_restricted_field(mdr_models.ObjectClass)
        mf = CustomField.objects.get_for_model(mdr_models.ObjectClass, user=self.su)
        self.assertCountEqual(mf, [self.authfield, self.allfield, self.wgfield, self.rafield, rf])

    def test_get_fields_for_model_different_model_for_super(self):
        self.make_restricted_field(mdr_models.ObjectClass)
        mf = CustomField.objects.get_for_model(mdr_models.DataElement, user=self.su)
        self.assertCountEqual(mf, [self.authfield, self.allfield, self.wgfield, self.rafield])

    def test_get_fields_for_model_for_editor(self):
        rf = self.make_restricted_field(mdr_models.ObjectClass)
        mf = CustomField.objects.get_for_model(mdr_models.ObjectClass, user=self.editor)
        self.assertCountEqual(mf, [self.authfield, self.allfield, self.wgfield, rf])

    def test_get_fields_for_model_different_model_for_editor(self):
        self.make_restricted_field(mdr_models.ObjectClass)
        mf = CustomField.objects.get_for_model(mdr_models.DataElement, user=self.editor)
        self.assertCountEqual(mf, [self.authfield, self.allfield, self.wgfield])


class CustomFieldsStatusTestCase(AristotleTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        self.active_item = mdr_models.ObjectClass.objects.create(
            submitter=self.editor,
            name='Person',
            definition='A Human',
            workgroup=self.wg1
        )

        self.inactive_item = mdr_models.ObjectClass.objects.create(
            submitter=self.editor,
            name='Person',
            definition='A Human',
            workgroup=self.wg1
        )

        # An item with no Custom Value associated for the inactive Custom Field
        self.inactive_item_with_no_value = mdr_models.ObjectClass.objects.create(
            submitter=self.editor,
            name='Person',
            definition='A Human',
            workgroup=self.wg1
        )

        self.inactive_item_with_empty_int_field = mdr_models.ObjectClass.objects.create(
            submitter=self.editor,
            name='Person',
            definition='A Human',
            workgroup=self.wg1
        )

        self.hidden_item = mdr_models.ObjectClass.objects.create(
            submitter=self.editor,
            name='Person',
            definition='A Human',
            workgroup=self.wg1
        )

        self.activefield = CustomField.objects.create(
            order=0,
            name='ActiveField',
            type='str',
            state=CUSTOM_FIELD_STATES.active
        )
        self.inactivefield = CustomField.objects.create(
            order=1,
            name='InactiveField',
            type='int',
            state=CUSTOM_FIELD_STATES.inactive
        )
        self.hiddenfield = CustomField.objects.create(
            order=2,
            name='HiddenField',
            type='str',
            state=CUSTOM_FIELD_STATES.hidden,
        )

        self.active_value = CustomValue.objects.create(
            field=self.activefield,
            concept=self.active_item,
            content='Active'
        )

        self.inactive_value = CustomValue.objects.create(
            field=self.inactivefield,
            concept=self.inactive_item,
            content='Inactive'
        )

        self.inactive_value_empty_int = CustomValue.objects.create(
            field=self.inactivefield,
            concept=self.inactive_item_with_empty_int_field,
            content=''
        )

        self.hidden_value = CustomValue.objects.create(
            field=self.hiddenfield,
            concept=self.hidden_item,
            content='Hidden'
        )

    def test_editing_active_custom_field(self):
        # Check that the editor can edit an active custom field
        self.login_editor()

        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.active_item.id],
            status_code=200
        )

        fields = response.context['form'].fields
        self.assertTrue(self.activefield.form_field_name in fields)

    def test_viewing_active_custom_field(self):
        # Check that the viewer can view an active custom field
        self.login_viewer()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.active_item.id, 'objectclass', 'person'],
            status_code=200
        )
        # Check that the active value is showing up
        self.assertEqual(len(response.context['custom_values']), 1)

    def test_viewing_inactive_field_with_content(self):
        # Users should still be able to view inactive custom field with content
        self.login_viewer()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.inactive_item.id, 'objectclass', 'person'],
            status_code=200
        )
        self.assertEqual(len(response.context['custom_values']), 1)

    def test_editor_cant_edit_empty_inactive_field(self):
        # An editor should not be able to edit an inactive custom field with no CustomValue associated
        self.login_editor()

        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.inactive_item_with_no_value.id],
            status_code=200
        )

        fields = response.context['form'].fields
        # The inactive field shouldn't show up
        self.assertFalse(self.inactivefield.form_field_name in fields)

    def test_editor_can_edit_inactive_field_with_content(self):
        # An editor should still be able to edit an inactive custom field if it has previously been
        # filled with content
        self.login_editor()

        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.inactive_item.id],
            status_code=200
        )

        fields = response.context['form'].fields
        self.assertTrue(self.inactivefield.form_field_name in fields)

    def test_editor_cant_edit_inactive_int_field_with_no_content(self):
        # An editor should not be able to edit an inactive integer field with no content
        self.login_editor()

        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.inactive_item_with_empty_int_field.id],
            status_code=200
        )

        fields = response.context['form'].fields
        self.assertFalse(self.inactivefield.form_field_name in fields)

    def test_viewer_cant_view_hidden_field(self):
        # A viewer should not be able to see a custom field if it has been hidden
        self.login_viewer()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.hidden_item.id, 'objectclass', 'person'],
            status_code=200
        )
        self.assertEqual(len(response.context['custom_values']), 0)

    def test_editor_cant_edit_hidden_field(self):
        # An editor should not be able to edit a custom field if it has been hidden
        self.login_editor()

        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.hidden_item.id],
            status_code=200
        )

        fields = response.context['form'].fields

        self.assertFalse(self.hiddenfield.form_field_name in fields)

    def test_superuser_can_see_hidden_fields(self):
        # A superuser should be able to see hidden custom fields
        self.login_superuser()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.hidden_item.id, 'objectclass', 'person'],
            status_code=200
        )
        self.assertEqual(len(response.context['custom_values']), 1)

    def test_superuser_can_edit_empty_inactive_fields(self):
        # A superuser should be able to edit inactive hidden fields
        self.login_superuser()

        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.inactive_item_with_no_value.id],
            status_code=200,
        )
        fields = response.context['form'].fields

        self.assertTrue(self.inactivefield.form_field_name in fields)

    def test_superuser_can_edit_hidden_fields(self):
        self.login_superuser()

        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.hidden_item.id],
            status_code=200,
        )
        fields = response.context['form'].fields

        self.assertTrue(self.hiddenfield.form_field_name in fields)
