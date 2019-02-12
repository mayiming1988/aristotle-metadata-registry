from aristotle_mdr.fields import LowerEmailField
from improved_user.model_mixins import AbstractUser

from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    email = LowerEmailField(_('email address'), max_length=254, unique=True)

    @property
    def first_name(self):
        return self.short_name

    @property
    def last_name(self):
        return self.full_name

    class ReportBuilder:
        exclude = ('password',)
