from django.test import TestCase
from aristotle_mdr.tests.utils import AristotleTestUtils

from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomFieldsTestCase(AristotleTestUtils, TestCase):

    def test_create_custom_field_normal_user(self):
        self.login_editor()
        response = self.reverse_get(
            'aristotle_custom_fields:create',
            status_code=302
        )
        self.assertTrue(response.url.startswith('/login'))

    def test_create_custom_field(self):
        self.login_superuser()
        postdata = {
            'name': 'Spiciness',
            'type': 'str',
            'help_text': 'The spiciness of the metadata'
        }
        response = self.reverse_post(
            'aristotle_custom_fields:create',
            postdata,
            status_code=302
        )
        # print(response.context['form'].errors)
        self.assertEqual(CustomField.objects.count(), 1)
        cf = CustomField.objects.first()
        self.assertEqual(cf.name, 'Spiciness')
        self.assertEqual(cf.type, 'str')
        self.assertEqual(cf.help_text, postdata['help_text'])
