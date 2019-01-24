from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR
from aristotle_mdr.fields import ConceptOneToOneField
from aristotle_mdr.constants import visibility_permission_choices


class VersionPublicationRecord(TimeStampedModel):
    class Meta:
        unique_together = (
            ("content_type", "object_id"),
        )
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

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


class PublicationRecord(TimeStampedModel):
    class Meta:
        unique_together = (
            ("content_type", "object_id"),
        )
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    publisher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="published_content"
    )
    permission = models.IntegerField(
        choices=visibility_permission_choices,
        default=visibility_permission_choices.public
    )
    publication_date = models.DateField(
        default=timezone.now,
        help_text=_("Enter a date in the future to specify the date is published from.")
    )
