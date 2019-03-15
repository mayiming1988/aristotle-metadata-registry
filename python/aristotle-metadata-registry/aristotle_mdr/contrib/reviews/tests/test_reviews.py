from django.test import TestCase
import aristotle_mdr.tests.utils as utils
from django.core.cache import cache
from aristotle_mdr import models
from aristotle_mdr.contrib.reviews.forms import RequestReviewCreateForm
from aristotle_mdr.contrib.reviews.models import ReviewRequest
import logging

logger = logging.getLogger(__name__)


class ReviewsFormsTest(utils.AristotleTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        cache.clear()

    def test_inactive_registration_authoritites_dont_appear_as_options_in_form(self):
        self.login_regular_user()
        self.item1 = models.ObjectClass.objects.create(
            name="Test Item 1", definition="my definition")
        self.my_active_ra = models.RegistrationAuthority.objects.create(name="My Active RA",
                                                                 definition="",
                                                                 stewardship_organisation=self.steward_org_1,
                                                                 active=0)
        self.my_inactive_ra = models.RegistrationAuthority.objects.create(name="My Inactive RA",
                                                                        definition="",
                                                                        stewardship_organisation=self.steward_org_1,
                                                                        active=1)
        self.my_hidden_ra = models.RegistrationAuthority.objects.create(name="My Hidden RA",
                                                                          definition="",
                                                                          stewardship_organisation=self.steward_org_1,
                                                                          active=2)

        self.review_request = ReviewRequest.objects.create(registration_authority=self.my_active_ra, requester_id=self.newuser.id)
        self.form = RequestReviewCreateForm(
            user=self.newuser
        )
        self.form.instance = self.review_request

        self.assertIn(self.my_active_ra, self.form.fields['registration_authority'].queryset)
        self.assertNotIn(self.my_inactive_ra, self.form.fields['registration_authority'].queryset)
        self.assertNotIn(self.my_hidden_ra, self.form.fields['registration_authority'].queryset)
