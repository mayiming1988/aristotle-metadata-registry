from django.test import TestCase, tag

from aristotle_mdr.validators import RegexValidator


class ValidationTests(TestCase):

    def test_regex_validator(self):

        # Test validator for 4 length word
        validator = RegexValidator(r'\w{4}')

        self.assertTrue(validator.validate('yeah'))
        self.assertFalse(validator.validate('yea'))
        self.assertFalse(validator.validate('yeahh'))
