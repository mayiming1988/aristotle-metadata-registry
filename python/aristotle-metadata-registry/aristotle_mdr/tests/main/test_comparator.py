from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.tests.utils as utils


class ComparatorTester(utils.LoggedInViewPages):
    def setUp(self):
        super().setUp()
        self.steward_org_1 = models.StewardOrganisation.objects.create(name="Test SO")

        self.ra = models.RegistrationAuthority.objects.create(name="Test RA", stewardship_organisation=self.steward_org_1)

        self.wg = models.Workgroup.objects.create(name="Setup WG", stewardship_organisation=self.steward_org_1)

        self.item1 = self.itemType.objects.create(name="Item with a name", workgroup=self.wg)

        self.item2 = self.itemType.objects.create(name="Item with a different name", workgroup=self.wg)

    def test_compare_with_no_selections_shows_blank_form(self):
        pass

    def test_user_without_permission_cant_compare_items(self):
        pass

    def test_concept_with_no_version_handled(self):
        pass

    def test_user_can_compare_different_dss_objects(self):
        pass
        # TODO: Make a test that compares two DSS's and identifies different Data Elements

    def test_user_can_compare_different_distribution_objects(self):
        pass
        # TODO: Make a test that compares two Distributions and identifies different Data Elements
