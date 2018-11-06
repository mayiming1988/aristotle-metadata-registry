from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel

from aristotle_mdr import models as MDR
from aristotle_mdr.contrib.async_signals.utils import fire


class BusinessRule(TimeStampedModel):
    registration_authority = models.ForeignKey(MDR.RegistrationAuthority, related_name="business_rules")
    name = models.TextField()
    description = models.TextField(null=True)
    ruleset = models.TextField(null=True)
    active = models.BooleanField()
