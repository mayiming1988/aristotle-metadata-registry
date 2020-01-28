from django import forms

import aristotle_mdr.models as MDR
from aristotle_mdr.forms.utils import StewardOrganisationRestrictedChoicesForm


class CreateRegistrationAuthorityForm(StewardOrganisationRestrictedChoicesForm):
    class Meta:
        model = MDR.RegistrationAuthority
        fields = ['name', 'definition', 'stewardship_organisation']


class EditRegistationAuthorityForm(forms.ModelForm):
    class Meta:
        model = MDR.RegistrationAuthority
        fields = [
            'locked_state',
            'public_state',
            'notprogressed',
            'incomplete',
            'candidate',
            'recorded',
            'qualified',
            'standard',
            'preferred',
            'superseded',
            'retired',
        ]

    def clean(self):
        cleaned_data = super().clean()

        # Locked must be lower than public
        if cleaned_data['locked_state'] >= cleaned_data['public_state']:
            raise forms.ValidationError('Locked state must be lower than public state')
