from django import forms
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _

import aristotle_mdr.models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareModelForm, UserAwareForm
from aristotle_mdr.forms.forms import ChangeStatusGenericForm
from django.core.exceptions import ValidationError

from aristotle_mdr.forms.bulk_actions import LoggedInBulkActionForm
from aristotle_mdr.models import _concept
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker

from . import models


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


class RequestReviewCancelForm(UserAwareModelForm):
    class Meta:
        model = models.ReviewRequest
        fields = []


class RequestReviewRejectForm(UserAwareModelForm):
    class Meta:
        model = models.ReviewRequest
        fields = []


class RequestReviewAcceptForm(UserAwareForm):
    response = forms.CharField(
        max_length=512,
        required=False,
        label=_("Reply to the original review request below."),
        widget=forms.Textarea
    )


class RequestCommentForm(UserAwareModelForm):
    class Meta:
        model = models.ReviewComment
        fields = ['body']


class RequestReviewBulkActionForm(LoggedInBulkActionForm, RequestReviewForm):
    confirm_page = "aristotle_mdr/actions/bulk_actions/request_review.html"
    classes="fa-flag"
    action_text = _('Request review')
    items_label = "These are the items that will be reviewed. Add or remove additional items with the autocomplete box."

    def make_changes(self):
        import reversion
        ra = self.cleaned_data['registrationAuthorities']
        state = self.cleaned_data['state']
        items = self.items_to_change
        cascade = self.cleaned_data['cascadeRegistration']
        registration_date = self.cleaned_data['registrationDate']
        message = self.cleaned_data['changeDetails']

        with transaction.atomic(), reversion.revisions.create_revision():
            reversion.revisions.set_user(self.user)

            review = models.ReviewRequest.objects.create(
                requester=self.user,
                registration_authority=ra,
                registration_date=registration_date,
                message=message,
                state=state,
                due_date = self.cleaned_data['due_date'],
                cascade_registration=cascade
            )
            failed = []
            success = []
            for item in items:
                if item.can_view(self.user):
                    success.append(item)
                else:
                    failed.append(item)

            review.concepts = success

            user_message = mark_safe(_(
                "%(num_items)s items requested for review - <a href='%(url)s'>see the review here</a>."
            ) % {
                'num_items': len(success),
                'url': reverse('aristotle_reviews:userReviewDetails', args=[review.id])
            })
            reversion.revisions.set_comment(message + "\n\n" + user_message)
            return user_message
