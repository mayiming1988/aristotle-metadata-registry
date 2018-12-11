"""
Aristotle MDR 11179 Slots models
================================

These are based on the Slots definition in ISO/IEC 11179 Part 3 - 7.2.2.4
"""

from django.db import models

from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR
from aristotle_mdr.fields import ConceptForeignKey

from aristotle_mdr.contrib.slots.choices import permission_choices
from aristotle_mdr.contrib.slots.manager import SlotsManager


class Slot(TimeStampedModel):
    # on save confirm the concept and model are correct, otherwise reject
    # on save confirm the cardinality
    name = models.CharField(max_length=256)  # Or some other sane length
    type = models.CharField(max_length=256, blank=True)  # Or some other sane length
    concept = ConceptForeignKey(MDR._concept, related_name='slots')
    value = models.TextField()
    order = models.PositiveSmallIntegerField("Position", default=0)
    permission = models.IntegerField(
        choices=permission_choices,
        default=permission_choices.public
    )

    objects = SlotsManager()

    @property
    def hr_permission(self):
        """Human readable permission"""
        return permission_choices[self.permission]

    def __str__(self):
        return u"{0} - {1}".format(self.name, self.value)

    class Meta:
        ordering = ['order']
