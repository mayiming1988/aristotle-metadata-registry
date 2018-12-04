from django.test import TestCase
from aristotle_mdr.tests.utils import AristotleTestUtils

from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldsTestCase(AristotleTestUtils, TestCase):

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
