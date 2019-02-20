from django import forms
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareModelForm, UserAwareForm
from aristotle_mdr.forms.forms import ChangeStatusGenericForm

from aristotle_mdr.forms.bulk_actions import LoggedInBulkActionForm, RedirectBulkActionMixin
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
from aristotle_mdr.contrib.autocomplete.widgets import (
    ConceptAutocompleteSelectMultiple,
    ConceptAutocompleteSelect
)

from . import models

import logging
logger = logging.getLogger(__name__)


class RequestReviewForm(ChangeStatusGenericForm):

    due_date = forms.DateField(
        required=False,
        label=_("Due date"),
        widget=BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
        initial=timezone.now()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_registration_authority_field(
            field_name='registrationAuthorities'
        )

    def clean_registrationAuthorities(self):
        value = self.cleaned_data['registrationAuthorities']
        return MDR.RegistrationAuthority.objects.get(id=int(value))


class RequestReviewCreateForm(UserAwareModelForm):
    class Meta:
        model = models.ReviewRequest
        fields = [
            'registration_authority', 'title', 'due_date', 'target_registration_state',
            'registration_date', 'concepts',
            'cascade_registration'
        ]
        widgets = {
            'title': forms.Textarea(),
            'target_registration_state': forms.RadioSelect(),
            'due_date': BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
            'registration_date': BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
            'concepts': ConceptAutocompleteSelectMultiple(),
            'cascade_registration': forms.RadioSelect(),
        }
        help_texts = {
            'target_registration_state': "The state for endorsement for metadata in this review",
            'due_date': "Date this review needs to be actioned by",
            'registration_date': "Date the metadata will be endorsed at",
            'title': "A short title for this review",
            'concepts': "List of concepts for review",
            'cascade_registration': "Include related items when registering metadata. When enabled, see the full list of metadata under the \"impact\" tab.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_registration_state'].choices = MDR.STATES
        self.fields['concepts'].queryset = self.fields['concepts'].queryset.all().visible(self.user)
        self.fields['concepts'].widget.choices = self.fields['concepts'].choices


class RequestReviewUpdateForm(UserAwareModelForm):
    class Meta:
        model = models.ReviewRequest
        fields = [
            'title', 'due_date', 'target_registration_state', 'registration_date', 'concepts',
            'cascade_registration'
        ]
        widgets = {
            'title': forms.Textarea(),
            'target_registration_state': forms.RadioSelect(),
            'due_date': BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
            'registration_date': BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
            'concepts': ConceptAutocompleteSelectMultiple(),
            'cascade_registration': forms.RadioSelect(),
        }
        help_texts = {
            'target_registration_state': "The state for endorsement for metadata in this review",
            'due_date': "Date this review needs to be actioned by",
            'registration_date': "Date the metadata will be endorsed at",
            'title': "A short title for this review",
            'concepts': "List of concepts for review",
            'cascade_registration': "Include related items when registering metadata. When enabled, see the full list of metadata under the \"impact\" tab.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['target_registration_state'].choices = MDR.STATES
        self.fields['concepts'].queryset = self.fields['concepts'].queryset.all().visible(self.user)
        self.fields['concepts'].widget.choices = self.fields['concepts'].choices


class RequestReviewAcceptForm(UserAwareForm):
    status_message = forms.CharField(
        required=False,
        label=_("Status message"),
        help_text=_("Describe why the status is being changed."),
        widget=forms.Textarea
    )
    close_review = forms.ChoiceField(
        initial=1,
        widget=forms.RadioSelect(),
        choices=[(0, _('No')), (1, _('Yes'))],
        label=_("Do you want to close this review?")
    )


class RequestReviewEndorseForm(RequestReviewAcceptForm):
    registration_state = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=MDR.STATES,
        label=_("Registration State"),
        help_text="The state for endorsement for metadata in this review",
    )
    registration_date = forms.DateField(
        widget=BootstrapDateTimePicker(options={"format": "YYYY-MM-DD"}),
        label=_("Registration Date"),
    )
    cascade_registration = forms.ChoiceField(
        initial=0,
        choices=[(0, _('No')), (1, _('Yes'))],
        label=_("Do you want to request a status change for associated items")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['close_review'].initial = 0


class RequestCommentForm(UserAwareModelForm):
    class Meta:
        model = models.ReviewComment
        fields = ['body']


class RequestReviewBulkActionForm(RedirectBulkActionMixin, LoggedInBulkActionForm, RequestReviewForm):
    classes="fa-flag"
    action_text = _('Request review')

    @classmethod
    def get_redirect_url(cls, request):
        from urllib.parse import urlencode
        items = request.POST.getlist("items")
        item_ids = MDR._concept.objects.visible(user=request.user).filter(id__in=items).values_list('id', flat=True)
        params = {'items': item_ids}
        return "{}?{}".format(
            reverse("aristotle_reviews:review_create"),
            urlencode(params, True)
        )


class ReviewRequestSupersedesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # Make only concepts in the review allowed as newer items
        if 'review_concepts' in kwargs:
            review_concepts = kwargs.pop('review_concepts')
            super().__init__(*args, **kwargs)
            self.fields['newer_item'].queryset = review_concepts
        else:
            super().__init__(*args, **kwargs)

    class Meta:
        fields = ('older_item', 'newer_item', 'message')
        widgets = {
            'older_item': ConceptAutocompleteSelect,
            'message': forms.widgets.TextInput
        }
