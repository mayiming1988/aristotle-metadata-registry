from django.test import TestCase

from aristotle_mdr.tests.utils import AristotleTestUtils
import aristotle_mdr.models as MDR


class VersionComparisionTestCase(AristotleTestUtils, TestCase):
    """Class to test the version comparision view"""
    def setUp(self):
        self.object_class = MDR.ObjectClass.objects.create(
            name='Person',
            definition='A human being',
            submitter=self.editor
        )

    def test_altered_on_concept_field_displayed(self):
        """Test that field that is **on** the concept, and has
        had content altered between the saves is displayed"""
        pass

    def test_added_subitem_displayed(self):
        """Test that a subitem (ex. custom fields) added to a concept between versions is displayed """

    def test_removed_subitem_displayed(self):
        """Test that a subitem (ex. custom fields) removed from a concept between versions is displayed"""

    def test_changed_subitem_displayed(self):
        """Test that a subitem (ex. custom fields) that has had content on it altered is displayed """

    def test_version_chronology_correct(self):
        """Test that the versions are compared with the correct chronology"""


class DataElementComparisionTestCase(AristotleTestUtils, TestCase):
    """Class to test the comparision of Value Domain specific fields"""
    def test_value_domain_changes_displayed(self):
        """Test that values displayed are """
        pass


class HTMLFieldComparisionTestCase(AristotleTestUtils, TestCase):
    def setUp(self):
        pass


class ListVersionsTestCase(AristotleTestUtils, TestCase):
    def setUp(self):
        pass