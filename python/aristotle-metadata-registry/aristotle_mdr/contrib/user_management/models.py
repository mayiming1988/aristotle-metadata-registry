from improved_user.mixins import AbstractUser
from aristotle_mdr.fields import LowerEmailField
from django.db import models
from django.utils.translation import ugettext_lazy as _

class User(AbstractUser):
    email = LowerEmailField(_('email address'), max_length=254, unique=True)
