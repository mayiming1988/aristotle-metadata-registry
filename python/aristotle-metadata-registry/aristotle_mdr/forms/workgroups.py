from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.forms.creation_wizards import UserAwareForm, UserAwareModelForm

from aristotle_mdr.forms.utils import StewardOrganisationRestrictedChoicesForm, BootstrapableMixin


class AddMembers(forms.Form):
    role = forms.ChoiceField(
        label=_("Workgroup role"),
        choices=sorted(MDR.Workgroup.roles),
        widget=forms.Select
    )
    user = forms.ModelChoiceField(
        label=_("Select user"),
        queryset=get_user_model().objects.filter(is_active=True),
        widget=widgets.UserAutocompleteSelect()
    )

    def clean_roles(self):
        roles = self.cleaned_data['roles']
        roles = [role for role in roles if role in MDR.Workgroup.roles.keys()]
        return roles


class ChangeWorkgroupUserRolesForm(UserAwareForm):
    role = forms.ChoiceField(
        label=_("Workgroup role"),
        choices=sorted(MDR.Workgroup.roles),
        widget=forms.Select,
        required=False
    )


class CreateWorkgroupForm(StewardOrganisationRestrictedChoicesForm):
    class Meta:
        model = MDR.Workgroup
        fields = ['name', 'definition', 'stewardship_organisation']


class WorkgroupEditForm(BootstrapableMixin, UserAwareModelForm):
    class Meta:
        model = MDR.Workgroup
        fields = ['name', 'definition']
        widgets = {
            'name': forms.TextInput()
        }
