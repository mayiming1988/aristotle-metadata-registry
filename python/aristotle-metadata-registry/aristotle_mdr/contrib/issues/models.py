from django.db import models
from model_utils.models import TimeStampedModel

from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.models import _concept


class Issue(models.Model):

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
    isopen=models.BooleanField(
        default=True
    )
