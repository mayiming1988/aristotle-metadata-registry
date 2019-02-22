from django.test import TestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from aristotle_mdr.tests.utils import AristotleTestUtils

from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.slots.models import Slot
from aristotle_mdr.contrib.slots.choices import permission_choices
from aristotle_mdr.contrib.custom_fields.models import CustomField, CustomValue


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
        cf1 = CustomField.objects.create(
            order=0,
            name='CF1',
            type='str',
            help_text='Custom Field 1'
        )
        cf2 = CustomField.objects.create(
            order=1,
            name='CF2',
            type='str',
            help_text='Custom Field 2'
        )

        self.login_superuser()
        response = self.reverse_get(
            'aristotle_custom_fields:list',
            status_code=200
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
            type='String',
            visibility=permission_choices.public
        )
        self.authfield = CustomField.objects.create(
            order=1,
            name='AuthField',
            type='String',
            visibility=permission_choices.auth
        )
        self.wgfield = CustomField.objects.create(
            order=2,
            name='WgField',
            type='String',
            visibility=permission_choices.workgroup
        )

    def make_restricted_field(self, model):
        ct = ContentType.objects.get_for_model(model)
        restricted = CustomField.objects.create(
            order=3,
            name='Restricted',
            type='String',
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

    def test_get_fields_for_model(self):
        rf = self.make_restricted_field(mdr_models.ObjectClass)
        mf = CustomField.objects.get_for_model(mdr_models.ObjectClass)
        self.assertCountEqual(mf, [self.authfield, self.allfield, self.wgfield, rf])

    def test_get_fields_for_model_different_model(self):
        self.make_restricted_field(mdr_models.ObjectClass)
        mf = CustomField.objects.get_for_model(mdr_models.DataElement)
        self.assertCountEqual(mf, [self.authfield, self.allfield, self.wgfield])
