from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.forms import ModelForm, BooleanField

from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
import aristotle_mdr.models as MDR
from aristotle_mdr.perms import user_can_edit
from aristotle_mdr.forms.creation_wizards import UserAwareForm
from aristotle_mdr.forms.fields import ReviewChangesChoiceField, MultipleEmailField
from aristotle_mdr.contrib.autocomplete import widgets
from django_jsonforms.forms import JSONSchemaField

from django.forms.models import modelformset_factory

from .utils import RegistrationAuthorityMixin


class ChangeStatusGenericForm(RegistrationAuthorityMixin, UserAwareForm):
    state = forms.ChoiceField(choices=MDR.STATES, widget=forms.RadioSelect)
    registrationDate = forms.DateField(
        required=False,
        label=_("Registration date"),
        widget=BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
        initial=timezone.now()
    )
    cascadeRegistration = forms.ChoiceField(
        initial=0,
        choices=[(0, _('No')), (1, _('Yes'))],
        label=_("Do you want to request a status change for associated items")
    )
    changeDetails = forms.CharField(
        max_length=512,
        required=False,
        label=_("Why is the status being changed for these items?"),
        widget=forms.Textarea
    )
    registrationAuthorities = forms.ChoiceField(
        label="Registration Authorities",
        choices=MDR.RegistrationAuthority.objects.none(),
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_registration_authority_field(
            field_name="registrationAuthorities", qs=self.user.profile.registrarAuthorities.filter(active=0)
        )


class ChangeStatusForm(ChangeStatusGenericForm):

    def clean_cascadeRegistration(self):
        return self.cleaned_data['cascadeRegistration'] == "1"

    def clean_registrationAuthorities(self):
        value = self.cleaned_data['registrationAuthorities']
        return [
            MDR.RegistrationAuthority.objects.get(id=int(value))
        ]

    def clean_state(self):
        state = self.cleaned_data['state']
        state = int(state)
        MDR.STATES[state]
        return state


class ReviewChangesForm(forms.Form):

    def __init__(self, queryset, static_content, ra, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['selected_list'] = ReviewChangesChoiceField(
            queryset=queryset,
            static_content=static_content,
            ra=ra,
            user=user,
            label=_("Select the items you would like to update")
        )


# Thanks http://stackoverflow.com/questions/6958708/grappelli-to-hide-sortable-field-in-inline-sortable-django-admin
class PermissibleValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = MDR.PermissibleValue
        fields = "__all__"


class CompareConceptsForm(forms.Form):
    item_a = forms.ModelChoiceField(
        queryset=MDR._concept.objects.none(),
        empty_label="None",
        label=_("First item"),
        required=True,
        widget=widgets.ConceptAutocompleteSelect()
    )
    item_b = forms.ModelChoiceField(
        queryset=MDR._concept.objects.none(),
        empty_label="None",
        label=_("Second item"),
        required=True,
        widget=widgets.ConceptAutocompleteSelect()
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.qs = kwargs.pop('qs').visible(self.user)
        super().__init__(*args, **kwargs)

        self.fields['item_a'] = forms.ModelChoiceField(
            queryset=self.qs,
            empty_label="None",
            label=_("First item"),
            required=True,
            widget=widgets.ConceptAutocompleteSelect()
        )
        self.fields['item_b']=forms.ModelChoiceField(
            queryset=self.qs,
            empty_label="None",
            label=_("Second item"),
            required=True,
            widget=widgets.ConceptAutocompleteSelect()
        )


class EditUserForm(ModelForm):

    profile_picture = MDR.PossumProfile._meta.get_field('profilePicture').formfield()

    class Meta:

        model = get_user_model()
        fields = ('email', 'full_name', 'short_name')
        labels = {
            'short_name': 'Display Name'
        }


class NotificationPermissionsForm(forms.Form):

    notifications_json = JSONSchemaField(
        schema={
            "type": "object",
            "title": "Notification Permissions",
            "properties": {
                "metadata changes": {
                    "type": "object",
                    "title": "Metadata Changes",
                    "properties": {
                        "general changes": {
                            "type": "object",
                            "title": "",
                            "description": "notify me of changes to:",
                            "properties": {
                                "items in my workgroups": {
                                    "title": "items in my workgroups",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "default": True
                                },
                                "items I have tagged / favourited": {
                                    "title": "items I have tagged / favourited",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "default": True
                                },
                                "any items I can edit": {
                                    "title": "any items I can edit",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "default": True
                                }
                            }
                        },
                        "superseded": {
                            "type": "object",
                            "title": "",
                            "description": "Notify me when the following metadata is superseded:",
                            "properties": {
                                "items in my workgroups": {
                                    "title": "items in my workgroups",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "default": True
                                },
                                "items I have tagged / favourited": {
                                    "title": "items I have tagged / favourited",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "default": True
                                },
                                "any items I can edit": {
                                    "title": "any items I can edit",
                                    "type": "boolean",
                                    "format": "checkbox",
                                    "default": True
                                }
                            }
                        }
                    }
                },
                "notification methods": {
                    "type": "object",
                    "title": "Notification Methods",
                    "description": "Notify me using the following methods:",
                    "properties": {
                        "email": {
                            "title": "Email",
                            "type": "boolean",
                            "format": "checkbox",
                            "default": False
                        },
                        "within aristotle": {
                            "title": "Within Aristotle",
                            "type": "boolean",
                            "format": "checkbox",
                            "default": True
                        }
                    }
                }
            }
        },
        options={
            'theme': 'bootstrap3',
            'disable_properties': True,
            'disable_collapse': True,
            'disable_edit_json': True,
            'no_additional_properties': True
        },
        label=''
    )


class ShareLinkForm(forms.Form):

    emails = MultipleEmailField(required=False)
    notify_new_users_checkbox = BooleanField(label="Notify new people", initial=True, required=False)
