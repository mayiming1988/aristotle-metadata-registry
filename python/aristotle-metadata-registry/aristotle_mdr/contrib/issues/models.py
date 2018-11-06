from django.db import models
from django.conf import settings
from model_utils.models import TimeStampedModel

from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.models import _concept


class Issue(TimeStampedModel):

    name=models.CharField(
        max_length=1000
    )
    description=models.TextField(
        blank=True
    )
    item=ConceptForeignKey(
        _concept,
        related_name='issues'
    )
    submitter=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='issues'
    )
    isopen=models.BooleanField(
        default=True
    )

    def can_edit(self, user):
        return user.id == submitter.id

    def can_view(self, user):
        return self.item.can_view(user)

    def can_delete(self, user):
        return self.can_view(user)
