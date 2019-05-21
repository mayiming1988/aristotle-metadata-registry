from rest_framework.test import APIClient
from django.urls import reverse
from django.test import tag
from django.core.cache import cache
from aristotle_mdr_api.v4.tests import BaseAPITestCase
from aristotle_mdr.contrib.validators.models import RegistryValidationRules, RAValidationRules
from aristotle_mdr import models as mdr_models
import json


class RulesAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.ra = mdr_models.RegistrationAuthority.objects.create(
            name='My RA',
            definition='My very own',
            stewardship_organisation=self.so
        )
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

    def tearDown(self):
        cache.clear()

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
        self.login_superuser()
        response = self.client.put(
            reverse('api_v4:registry_rules'),
            {'rules': 'This aint yaml: ---:-:'},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_valid_ra_rules(self):
        self.ra.managers.add(self.user)
        self.login_user()
        response = self.client.post(
            reverse('api_v4:create_ra_rules'),
            {'registration_authority': self.ra.id, 'rules': self.valid_rules}
        )
        self.assertEqual(response.status_code, 201)
        r = RAValidationRules.objects.get(registration_authority=self.ra)
        self.assertEqual(r.rules, self.valid_rules)

    def test_create_ra_rules_non_manager(self):
        self.login_user()
        response = self.client.post(
            reverse('api_v4:create_ra_rules'),
            {'registration_authority': self.ra.id, 'rules': self.valid_rules}
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(json.loads(response.content)['registration_authority'][0].startswith('You don\'t have permission'))

    def test_edit_ra_rules(self):
        self.ra.managers.add(self.user)
        rules = RAValidationRules.objects.create(
            registration_authority=self.ra,
            rules=''
        )
        self.login_user()
        response = self.client.put(
            reverse('api_v4:ra_rules', args=[rules.id]),
            {'registration_authority': self.ra.id, 'rules': self.valid_rules},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        rules = RAValidationRules.objects.get(id=rules.id)
        self.assertEqual(rules.rules, self.valid_rules)

    def test_edit_ra_rules_not_manager(self):
        rules = RAValidationRules.objects.create(
            registration_authority=self.ra,
            rules=''
        )
        self.login_user()
        response = self.client.put(
            reverse('api_v4:ra_rules', args=[rules.id]),
            {'registration_authority': self.ra.id, 'rules': self.valid_rules},
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_edit_ra_rules_switch_ra(self):
        self.ra.managers.add(self.user)
        newra = mdr_models.RegistrationAuthority.objects.create(
            name='Brand new RA',
            definition='Brand new',
            stewardship_organisation=self.so
        )
        rules = RAValidationRules.objects.create(
            registration_authority=self.ra,
            rules=''
        )
        self.login_user()
        response = self.client.put(
            reverse('api_v4:ra_rules', args=[rules.id]),
            {'registration_authority': newra.id, 'rules': self.valid_rules},
            format='json'
        )
        self.assertEqual(response.status_code, 400)
