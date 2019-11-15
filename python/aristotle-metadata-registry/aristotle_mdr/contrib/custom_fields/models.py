"""
Aristotle MDR 11179 Slots with alternate management
Defined as a field by registry administrator
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models.signals import pre_save

from model_utils.models import TimeStampedModel

from aristotle_mdr.models import _concept, RichTextField
from aristotle_mdr.fields import ConceptForeignKey
from aristotle_mdr.constants import visibility_permission_choices as permission_choices

from aristotle_mdr.contrib.custom_fields.managers import CustomValueManager, CustomFieldManager
from aristotle_mdr.contrib.custom_fields.types import type_choices
from aristotle_mdr.contrib.custom_fields.constants import CUSTOM_FIELD_STATES
from aristotle_mdr.contrib.custom_fields.utils import get_system_name, generate_random_unique_characters


class CustomField(TimeStampedModel):
    order = models.IntegerField()
    name = models.CharField(max_length=1000)
    type = models.CharField(max_length=10, choices=type_choices)
    # A unique name used in identifying custom fields in the database in a meaningful way
    system_name = models.CharField(max_length=1000,
                                   unique=True,
                                   help_text='A name used for uniquely identifying the custom field',
                                   default='')
    # Optional
    help_text = models.CharField(max_length=1000, blank=True)
    help_text_long = RichTextField(
        blank=True,
        help_text="Longer contextual help and business rules describing a field.",
    )
    allowed_model = models.ForeignKey(
        ContentType, blank=True, null=True,
        on_delete=models.PROTECT
    )

    visibility = models.IntegerField(
        choices=permission_choices,
        default=permission_choices.public
    )

    state = models.IntegerField(
        choices=CUSTOM_FIELD_STATES,
        default=CUSTOM_FIELD_STATES.active
    )
    choices = models.CharField(blank=True, max_length=1000)

    objects = CustomFieldManager()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "CustomField with name: '{}' and allowed_model: '{}'".format(self.name, self.allowed_model)

    @property
    def hr_type(self):
        """Human readable type"""
        return type_choices[self.type]

    @property
    def hr_visibility(self):
        """Human readable visibility"""
        return permission_choices[self.visibility]

    @property
    def form_field_name(self):
        """The name used in forms for this field"""
        return 'custom_{name}_{id}'.format(name=self.name, id=self.id)

    def can_view(self, user):
        return user.is_superuser

    def can_edit(self, user):
        return user.is_superuser


class CustomValue(TimeStampedModel):
    field = models.ForeignKey(CustomField, related_name='values', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    concept = ConceptForeignKey(_concept, on_delete=models.CASCADE)

    objects = CustomValueManager()

    class Meta:
        ordering = ['field__order']
        unique_together = ('field', 'concept')

    @property
    def is_html(self):
        return self.field.type == 'html'

    def __str__(self):
        return 'CustomValue with field "{}" for concept "{}"'.format(self.field, self.concept)


@receiver(pre_save, sender=CustomField)
def set_system_name_if_none(sender, instance, **kwargs):
    if not instance.system_name:
        system_name = get_system_name(instance.allowed_model, instance.name)

        while CustomField.objects.filter(system_name=system_name).count() != 0:
            # Ensure that the generated system name is unique
            system_name = '{system_name}_{random_chars}'.format(system_name=system_name,
                                                                random_chars=generate_random_unique_characters())
        instance.system_name = system_name
