from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.forms.creation_wizards import UserAwareForm, UserAwareFormMixin


class AddMembers(forms.Form):
    roles = forms.MultipleChoiceField(
        label=_("Workgroup roles"),
        choices=sorted(MDR.Workgroup.roles.items()),
        widget=forms.CheckboxSelectMultiple
    )
    users = forms.ModelMultipleChoiceField(
        label=_("Select users"),
        queryset=get_user_model().objects.filter(is_active=True),
        widget=widgets.UserAutocompleteSelectMultiple()
    )

    def clean_roles(self):
        roles = self.cleaned_data['roles']
        roles = [role for role in roles if role in MDR.Workgroup.roles.keys()]
        return roles


class ChangeWorkgroupUserRolesForm(UserAwareForm):
    roles = forms.MultipleChoiceField(
        label=_("Workgroup roles"),
        choices=sorted(MDR.Workgroup.roles.items()),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class CreateWorkgroupForm(UserAwareFormMixin, forms.ModelForm):
    class Meta:
        model = MDR.Workgroup
        fields = ['name', 'definition', 'stewardship_organisation']
        widgets = {
            "stewardship_organisation": forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from aristotle_mdr.models import StewardOrganisation, StewardOrganisationMembership
        kwargs = {
            "state__in": StewardOrganisation.active_states
        }
        if not self.user.is_superuser:
            kwargs.update({
                "members__user": self.user,
                "members__role": StewardOrganisation.roles.admin,
                
            })
        self.fields["stewardship_organisation"].queryset = StewardOrganisation.objects.filter(**kwargs)
