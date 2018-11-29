from django.db import models
from model_utils.models import TimeStampedModel

from aristotle_mdr.models import _concept
from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.contrib.custom_fields.types import type_choices


class CustomField(TimeStampedModel):
    name = models.CharField(max_length=1000)
    type = models.CharField(max_length=10, choices=type_choices)
    help_text = models.CharField(max_length=1000)

    @property
    def hr_type(self):
        """Human readable type"""
        return type_choices[self.type]


class CustomValue(TimeStampedModel):
    field = models.ForeignKey(CustomField)
    content = models.TextField()
    concept = ConceptForeignKey(_concept)

    @property
    def is_html(self):
        return self.field.type == 'html'
