from rest_framework.test import APIClient
from django.urls import reverse
from django.test import tag
from aristotle_mdr_api.v4.tests import BaseAPITestCase
from aristotle_mdr.contrib.validators.models import RegistryValidationRules


class RulesAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.valid_rules = (
            '- status: Standard\n'
            '  object: DataElement\n'
            '  checks:\n'
            '    - validator: RegexValidator\n'
            '      field: name\n'
            '      regex: "[abc]+"'
        )
        self.invalid_rules = (
            '- status: Standard\n'
            '  object: DataElement\n'
            '  checks: MakeSureWeGood'
        )

    def test_create_valid_registry_rules(self):
        self.login_superuser()
        response = self.client.put(
            reverse('api_v4:registry_rules'),
            {'rules': self.valid_rules},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        rr = RegistryValidationRules.objects.first()
        self.assertEqual(rr.rules, self.valid_rules)

    def test_create_registry_rules_as_standard_user(self):
        self.login_user()
        response = self.client.put(
            reverse('api_v4:registry_rules'),
            {'rules': self.valid_rules},
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_create_invalid_registry_rules(self):
        self.login_superuser()
        response = self.client.put(
            reverse('api_v4:registry_rules'),
            {'rules': self.invalid_rules},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_registry_rules_invalid_yaml(self):
        response = self.client.put(
            reverse('api_v4:registry_rules'),
            {'rules': 'This aint yaml: ---:-:'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
