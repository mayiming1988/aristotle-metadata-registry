from django.db import models
from model_utils.models import TimeStampedModel

from aristotle_mdr.models import _concept
from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.contrib.custom_fields.managers import CustomValueManager
from aristotle_mdr.contrib.custom_fields.types import type_choices


class CustomField(TimeStampedModel):
    order = models.IntegerField(unique=True)
    name = models.CharField(max_length=1000, unique=True)
    type = models.CharField(max_length=10, choices=type_choices)
    help_text = models.CharField(max_length=1000, blank=True)

    @property
    def hr_type(self):
        """Human readable type"""
        return type_choices[self.type]

    def can_view(self, user):
        return user.is_superuser

    def can_edit(self, user):
        return user.is_superuser


class CustomValue(TimeStampedModel):
    field = models.ForeignKey(CustomField)
    content = models.TextField()
    concept = ConceptForeignKey(_concept)

    objects = CustomValueManager()

    class Meta:
        unique_together = ('field', 'concept')

    @property
    def is_html(self):
        return self.field.type == 'html'
