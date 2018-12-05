from django.test import TestCase
from aristotle_mdr.tests.utils import AristotleTestUtils

from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldsTestCase(AristotleTestUtils, TestCase):

    def create_test_field(self):
        cf = CustomField.objects.create(
            order=0,
            name='Spicness',
            type='str',
            help_text='The spiciness of the metadata'
        )
        return cf

    def test_custom_fields_list(self):
        cf1 = CustomField.objects.create(
            name='CF1',
            type='str',
            help_text='Custom Field 1'
        )
        cf2 = CustomField.objects.create(
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

        self.assertEqual(flist[0][0], 'CF1')
        self.assertEqual(flist[1][0], 'CF2')

    def test_custom_field_delete(self):
        cf = self.create_test_field()
        self.login_superuser()
        response = self.reverse_post(
            'aristotle_custom_fields:delete',
            {},
            reverse_args=[cf.id],
            status_code=302
        )
        self.assertFalse(CustomField.objects.filter(id=cf.id).exists())
