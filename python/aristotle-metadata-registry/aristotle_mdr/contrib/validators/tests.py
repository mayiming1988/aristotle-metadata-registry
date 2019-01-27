from django.test import TestCase

import datetime


from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.validators import validators

from aristotle_mdr.utils import setup_aristotle_test_environment

setup_aristotle_test_environment()


class ValidationTester:
    def assertValid(self, result, expected_message=""):
        is_valid, actual_message = result
        self.assertTrue(is_valid)
        self.assertEqual(actual_message, expected_message)

    def assertNotValid(self, result, expected_message=""):
        is_valid, actual_message = result
        self.assertFalse(is_valid)
        self.assertEqual(actual_message, expected_message)


class TestBaseValidator(ValidationTester, TestCase):
    def test_validator_name(self):

        validator = validators.BaseValidator({
            'name': 'TestName'
        })

        self.assertEqual(validator.get_name(), 'TestName')

        validator = validators.BaseValidator({
            'validator': 'RegexValidator'
        })

        self.assertEqual(validator.get_name(), 'Unnamed RegexValidator')


class TestUniqueValuesValidator(ValidationTester, TestCase):

    def test_validator(self):
        employ = MDR.ValueDomain.objects.create(name="Employment Statuses", definition=".")
        a = MDR.PermissibleValue.objects.create(valueDomain=employ, value="e", meaning="Employed", order=1)
        b = MDR.PermissibleValue.objects.create(valueDomain=employ, value="u", meaning="Unemployed", order=2)
        c = MDR.PermissibleValue.objects.create(valueDomain=employ, value="u", meaning="Underemployed", order=3)

        self.assertNotValid(
            validators.UniqueValuesValidator(rule={}).validate(employ),
            expected_message="Value 'u' is a permissible value more than once - it appeared 2 times"
        )

        c.value="under"
        c.save()
        self.assertValid(
            validators.UniqueValuesValidator(rule={}).validate(employ),
        )


class TestRelationValidator(ValidationTester, TestCase):
    def test_invalid_rule(self):
        person_age = MDR.DataElementConcept.objects.create(name="Person-Age", definition=".")
        rule = {'field': 'name'}

        self.assertNotValid(
            validators.RelationValidator(
                rule=rule
            ).validate(person_age),
            expected_message=validators.RelationValidator.errors['NOT_FK'].format('name')
        )
        rule = {'field': 'fake_field'}

        self.assertNotValid(
            validators.RelationValidator(
                rule=rule
            ).validate(person_age),
            expected_message=validators.RelationValidator.errors['NOT_FOUND'].format('fake_field')
        )

    def test_validator(self):
        person = MDR.ObjectClass.objects.create(name="Person", definition=".")
        person_age = MDR.DataElementConcept.objects.create(name="Person-Age", definition=".")
        rule = {'field': 'property'}

        self.assertNotValid(
            validators.RelationValidator(
                rule=rule
            ).validate(person_age),
            expected_message=validators.RelationValidator.errors['NOT_LINKED'].format("property")
        )

        age = MDR.Property.objects.create(name="Age", definition=".")
        person_age.property = age
        self.assertValid(
            validators.RelationValidator(rule=rule).validate(person_age),
        )


class TestRegexValidator(ValidationTester, TestCase):
    def test_invalid_rule(self):
        self.assertNotValid(
            validators.RegexValidator(
                rule={}
            ).validate(None),
            expected_message="Invalid rule"
        )

    def test_validator(self):
        employ = MDR.ValueDomain.objects.create(name="employment Statuses", definition=".")
        rule = {'regex': '[A-Z].+', 'field': 'name'}

        self.assertNotValid(
            validators.RegexValidator(
                rule=rule
            ).validate(employ),
            expected_message="Text '{}' does not match required pattern.".format(employ.name)
        )

        employ.name = "Employment Status"
        employ.save()
        self.assertValid(
            validators.RegexValidator(rule=rule).validate(employ),
        )

    def test_regex_validator(self):
        self.item = MDR.ObjectClass(
            name='Test Object Class',
            definition=''
        )

        # Test validator for 4 length word
        validator = validators.RegexValidator({
            'name': 'regex',
            'field': 'name',
            'regex': r'\w{4}'
        })

        self.item.name = 'yeah'
        self.assertTrue(validator.validate(self.item)[0])

        self.item.name = 'yea'
        self.assertFalse(validator.validate(self.item)[0])

        self.item.name = 'yeahh'
        self.assertFalse(validator.validate(self.item)[0])


class TestStatusValidator(ValidationTester, TestCase):

    def setUp(self):
        self.steward_org_1 = MDR.StewardOrganisation.objects.create(
            name='Org 1',
            description="1",
        )
        self.item = MDR.ObjectClass.objects.create(
            name='Test Object Class',
            definition='Test Defn'
        )
        self.ra = MDR.RegistrationAuthority.objects.create(
            name='Test Content',
            definition='Only test content',
            stewardship_organisation=self.steward_org_1
        )

    def register_item_standard(self):
        # Register the item on 2 seperate dates to check that only most recent
        # is used
        MDR.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2014, 1, 1),
            state=MDR.STATES.incomplete
        )
        MDR.Status.objects.create(
            concept=self.item,
            registrationAuthority=self.ra,
            registrationDate=datetime.date(2014, 1, 2),
            state=MDR.STATES.standard
        )

    def test_status_validation_pass(self):
        self.register_item_standard()

        validator = validators.StatusValidator({
            'name': 'standard check',
            'status': ['Standard', 'Retired'],
        })

        self.assertValid(
            validator.validate(self.item, self.ra),
            expected_message='Valid State'
        )

    def test_status_validation_fail(self):
        self.register_item_standard()

        validator = validators.StatusValidator({
            'name': 'standard check',
            'status': ['NotProgressed', 'Incomplete'],
        })

        self.assertNotValid(
            validator.validate(self.item, self.ra),
            expected_message='Invalid State'
        )

    def test_status_validation_bad_state(self):
        # Test with an invalid state
        validator = validators.StatusValidator({
            'name': 'standard check',
            'status': ['MuchoBad', 'Incomplete'],
        })

        self.assertNotValid(
            validator.validate(self.item, self.ra),
            expected_message='Invalid rule'
        )

    def test_status_validation_no_ra(self):
        validator = validators.StatusValidator({
            'name': 'standard check',
            'status': ['Standard', 'Incomplete'],
        })

        self.assertNotValid(
            validator.validate(self.item, self.ra),
            expected_message='Invalid State'
        )
