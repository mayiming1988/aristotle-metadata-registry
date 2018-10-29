from django.test import TestCase, tag
from django.contrib.auth import get_user_model

from aristotle_mdr.validators import RegexValidator, BaseValidator, StatusValidator
from aristotle_mdr import models

import datetime


class ValidationTests(TestCase):

    def setUp(self):
        self.item = models.ObjectClass.objects.create(
            name='Test Object Class',
            definition='Test Defn'
        )
        self.ra = models.RegistrationAuthority.objects.create(
            name='Test Content',
            definition='Only test content'
        )

    def update_name(self, newname):
        self.item.name = newname
        self.item.save()

    def register_item_standard(self):
        # Register the item on 2 seperate dates to check that only most recent
        # is used
        models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2014, 1, 1),
            state=models.STATES.incomplete
        )
        models.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2014, 1, 2),
            state=models.STATES.standard
        )

    def test_validator_name(self):

        validator = BaseValidator({
            'name': 'TestName'
        })

        self.assertEqual(validator.getName(), 'TestName')

        validator = BaseValidator({
            'validator': 'RegexValidator'
        })

        self.assertEqual(validator.getName(), 'Unnamed RegexValidator')

    def test_regex_validator(self):

        # Test validator for 4 length word
        validator = RegexValidator({
            'name': 'regex',
            'field': 'name',
            'regex': r'\w{4}'
        })

        self.update_name('yeah')
        self.assertTrue(validator.validate(self.item)[0])

        self.update_name('yea')
        self.assertFalse(validator.validate(self.item)[0])

        self.update_name('yeahh')
        self.assertFalse(validator.validate(self.item)[0])

    def test_status_validation_pass(self):
        self.register_item_standard()

        validator = StatusValidator({
            'name': 'standard check',
            'status': ['Standard', 'Retired'],
        })

        status, message = validator.validate(self.item, self.ra)

        self.assertTrue(status)
        self.assertEqual(message, 'Valid State')

    def test_status_validation_fail(self):
        self.register_item_standard()

        validator = StatusValidator({
            'name': 'standard check',
            'status': ['NotProgressed', 'Incomplete'],
        })

        status, message = validator.validate(self.item, self.ra)

        self.assertFalse(status)
        self.assertEqual(message, 'Invalid State')

    def test_status_validation_bad_state(self):
        # Test with an invalid state
        validator = StatusValidator({
            'name': 'standard check',
            'status': ['MuchoBad', 'Incomplete'],
        })

        status, message = validator.validate(self.item, self.ra)
        self.assertFalse(status)
        self.assertEqual(message, 'Invalid rule')

    def test_status_validation_no_ra(self):
        validator = StatusValidator({
            'name': 'standard check',
            'status': ['Standard', 'Incomplete'],
        })

        status, message = validator.validate(self.item)
        self.assertFalse(status)
        self.assertEqual(message, 'Invalid rule')
