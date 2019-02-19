from django.test import TestCase
from aristotle_mdr.tests.utils import AristotleTestUtils

from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.reviews import models


class RRTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='My Object',
            definition='mine'
        )
        self.review = models.ReviewRequest.objects.create(
            registration_authority=self.ra,
            requester=self.editor,
            target_registration_state=mdr_models.STATES.standard
        )
        self.review.concepts.add(self.item)

    def test_rr_supersedes(self):
        self.login_editor()
        response = self.reverse_get(
            'aristotle_mdr_review_requests:request_supersedes',
            reverse_args=[self.review.pk]
        )
        self.assertEqual(response.status_code, 200)

    def test_rr_supersedes_formset_initial(self):
        self.login_editor()
        response = self.reverse_get(
            'aristotle_mdr_review_requests:request_supersedes',
            reverse_args=[self.review.pk],
            status_code=200
        )
        initial = response.context['formset'].initial
        self.assertCountEqual(
            initial,
            [{'newer_item': self.item.id}]
        )

    def test_rr_supersedes_create(self):
        # Add second item to review
        item2 = mdr_models.ObjectClass.objects.create(name='My 2nd Object', definition='mine')
        self.review.concepts.add(item2)
        # Create items to be used in supersede relation
        old1 = mdr_models.ObjectClass.objects.create(name='Old Object', definition='old')
        old2 = mdr_models.ObjectClass.objects.create(name='Old 2nd Object', definition='old')
        # Post data
        data = [
            {'older_item': old1.id, 'newer_item': self.item.id, 'message': 'wow'},
            {'older_item': old2.id, 'newer_item': item2.id, 'message': 'nice'},
        ]
        post_data = self.get_formset_postdata(data, initialforms=2)
        self.login_editor()
        response = self.reverse_post(
            'aristotle_mdr_review_requests:request_supersedes',
            post_data,
            reverse_args=[self.review.pk],
            status_code=302
        )
        # Check objects created
        self.review.refresh_from_db()
        review_supersedes = mdr_models.SupersedeRelationship.proposed_objects.filter(review=self.review)
        self.assertEqual(review_supersedes.count(), 2)
