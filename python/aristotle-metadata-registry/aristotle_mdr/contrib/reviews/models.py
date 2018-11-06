from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR
from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.contrib.async_signals.utils import fire
# from .signals import metadata_item_viewed

from aristotle_mdr.fields import (
    ShortTextField,
)


from aristotle_mdr.managers import (
    # MetadataItemManager, ConceptManager,
    ReviewRequestQuerySet,
    # WorkgroupQuerySet
)


REVIEW_STATES = Choices(
    (0, 'submitted', _('Submitted')),
    (5, 'cancelled', _('Cancelled')),
    (10, 'accepted', _('Accepted')),
    (15, 'rejected', _('Rejected')),
)


class ReviewRequest(TimeStampedModel):
    objects = ReviewRequestQuerySet.as_manager()
    concepts = models.ManyToManyField(
        MDR._concept, related_name="rr_review_requests"
    )
    registration_authority = models.ForeignKey(
        MDR.RegistrationAuthority,
        help_text=_("The registration authority the requester wishes to endorse the metadata item"),
        related_name='rr_requested_reviews'
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        help_text=_("The user requesting a review"),
        related_name='rr_requested_reviews'
    )
    workgroup = models.ForeignKey(
        MDR.Workgroup,
        help_text=_("A workgroup associated with this review"),
        related_name='rr_workgroup_reviews',
        null=True
    )
    message = models.TextField(blank=True, null=True, help_text=_("An optional message accompanying a request, this will accompany the approved registration status"))
    # reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, help_text=_("The user performing a review"), related_name='reviewed_requests')
    # response = models.TextField(blank=True, null=True, help_text=_("An optional message responding to a request"))
    status = models.IntegerField(
        choices=REVIEW_STATES,
        default=REVIEW_STATES.submitted,
        help_text=_('Status of a review')
    )
    state = models.IntegerField(
        choices=MDR.STATES,
        help_text=_("The state at which a user wishes a metadata item to be endorsed")
    )
    registration_date = models.DateField(
        _('Date registration effective'),
        help_text=_("date and time you want the metadata to be registered from")
    )
    due_date = models.DateField(
        _('Date response required'),
        help_text=_("Date and time a response is required"),
        null=True, blank=True
    )
    cascade_registration = models.IntegerField(
        choices=[(0, _('No')), (1, _('Yes'))],
        default=0,
        help_text=_("Update the registration of associated items")
    )

    def get_absolute_url(self):
        return reverse(
            "aristotle_reviews:userReviewDetails",
            kwargs={'review_id': self.pk}
        )

    def __str__(self):
        return "Review of {count} items as {state} in {ra} registraion authority".format(
            count=self.concepts.count(),
            state=self.get_state_display(),
            ra=self.registration_authority,
        )


class ReviewComment(TimeStampedModel):
    class Meta:
        ordering = ['created']

    request = models.ForeignKey(ReviewRequest, related_name='comments')
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
    )

    @property
    def edited(self):
        return self.created != self.modified


# class RegistrationAuthorityBusinessRule(TimeStampedModel):
#     registration_authority = models.ForeignKey(
#         MDR.RegistrationAuthority,
#         help_text=_("The registration authority the requester wishes to endorse the metadata item"),
#         related_name='validation_business_rules'
#     )
#     name = ShortTextField(
#         # help_text=_("An optional message accompanying a request, this will accompany the approved registration status")
#     )
#     rule = models.TextField(
#         # help_text=_("An optional message accompanying a request, this will accompany the approved registration status")
#     )
