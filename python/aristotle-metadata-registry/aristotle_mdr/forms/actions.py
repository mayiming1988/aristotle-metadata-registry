from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import BLANK_CHOICE_DASH

import aristotle_mdr.models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareForm
from aristotle_mdr.forms.forms import ChangeStatusGenericForm
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.perms import can_delete_metadata
from aristotle_mdr.models import _concept
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker


class RequestReviewForm(ChangeStatusGenericForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_registration_authority_field(
            field_name='registrationAuthorities'
        )

    def clean_registrationAuthorities(self):
        value = self.cleaned_data['registrationAuthorities']
        return MDR.RegistrationAuthority.objects.get(id=int(value))


class AddRegistrationUserForm(UserAwareForm):
    roles = forms.MultipleChoiceField(
        label=_("Registry roles"),
        choices=sorted(MDR.RegistrationAuthority.roles.items()),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    user = forms.ModelChoiceField(
        label=_("Select user"),
        queryset=get_user_model().objects.filter(is_active=True),
        widget=widgets.UserAutocompleteSelect(),
        initial=None,
    )


class ChangeRegistrationUserRolesForm(UserAwareForm):
    roles = forms.MultipleChoiceField(
        label=_("Registry roles"),
        choices=sorted(MDR.RegistrationAuthority.roles.items()),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class DeleteSandboxForm(UserAwareForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['item'] = forms.ModelChoiceField(
            label=_("Select item to delete"),
            queryset=_concept.objects.filter(submitter=self.user),
            required=True,
        )

    def clean_item(self):
        item = self.cleaned_data['item']

        if not can_delete_metadata(self.user, item):
            raise ValidationError("Item could not be deleted", code="invalid")

        return item


class SupersedeRelationshipFormBase(forms.ModelForm):
    """
    Base form class for SupersedeRelationship objects.
    """
    class Meta:
        model = MDR.SupersedeRelationship
        fields = ['older_item', 'registration_authority', 'message', 'date_effective']
        widgets = {
            'date_effective': BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
        }

    def __init__(self, *args, **kwargs):
        self.item = kwargs.pop('item')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['older_item'] = forms.ModelChoiceField(
            queryset=self.item._meta.model.objects.visible(self.user),
            empty_label=BLANK_CHOICE_DASH,
            label=_("Supersedes"),
            widget=widgets.ConceptAutocompleteSelect(
                model=self.item._meta.model
            )
        )

    def clean_older_item(self):
        item = self.cleaned_data['older_item']
        if not item:
            return None
        if self.item.id == item.id:
            raise forms.ValidationError("An item may not supersede itself")
        return item


class SupersedeRelationshipForm(SupersedeRelationshipFormBase):
    """
    SupersedeRelationship form with generic fields.
    """


class SupersedeRelationshipFormWithProposed(SupersedeRelationshipFormBase):
    """
    SupersedeRelationship form where user can change proposed status as well.
    """

    class Meta(SupersedeRelationshipFormBase.Meta):
        fields = ['older_item', 'registration_authority', 'proposed', 'message', 'date_effective']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict ra's to only ones user is a registrar in
        self.fields['registration_authority'] = forms.ModelChoiceField(
            queryset=self.user.profile.registrarAuthorities,
            empty_label=BLANK_CHOICE_DASH,
            label=_("Registration authority"),
        )
