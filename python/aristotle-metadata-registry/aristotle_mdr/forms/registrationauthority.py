from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.forms.creation_wizards import UserAwareForm, UserAwareFormMixin
from aristotle_mdr.forms.utils import StewardOrganisationRestrictedChoicesForm


class CreateRegistrationAuthorityForm(StewardOrganisationRestrictedChoicesForm):
    class Meta:
        model = MDR.RegistrationAuthority
        fields = ['name', 'definition', 'stewardship_organisation']
