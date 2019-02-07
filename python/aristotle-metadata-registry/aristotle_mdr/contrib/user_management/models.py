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

    def display_name(self):
        if self.short_name:
            return self.short_name
        if self.full_name:
            return self.full_name

        return self.censored_email

    @property
    def censored_email(self):
        return "{start}...{end}".format(
            start=self.email[:self.email.index('@') + 2],
            end=self.email[self.email.rindex('.') - 1:]
        )

    class ReportBuilder:
        exclude = ('password',)
