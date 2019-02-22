from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR
from aristotle_mdr.fields import ConceptOneToOneField


class VersionPublicationRecord(TimeStampedModel):
    concept = ConceptOneToOneField(
        MDR._concept, related_name='versionpublicationrecord',
        on_delete=models.deletion.CASCADE
    )
    public_user_publication_date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text=_("Date from which public users can view version histories for this item."),
        verbose_name=_("Public version history start date")
    )
    authenticated_user_publication_date = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text=_("Date from which logged in users can view version histories for this item."),
        verbose_name=_("Logged-in version history start date")
    )
