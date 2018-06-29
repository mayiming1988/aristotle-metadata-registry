from improved_user.mixins import AbstractUser
from django.db import models


class User(AbstractUser):

    pass

    @property
    def display_name(self):
        if self.short_name:
            return self.short_name
        if self.full_name:
            return self.short_name

        return self.censored_email

    @property
    def censored_email(self):
        return "{start}...{end}".format(
            start=self.email[:self.email.index('@')+2],
            end=self.email[self.email.rindex('.')-1:]
        )
