from django.db import models
from aristotle_mdr.models import RegistrationAuthority


class ValidationRules(models.Model):

    registration_authority = models.ForeignKey(RegistrationAuthority)
    rules = models.TextField()
