from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from aristotle_mdr.forms.utils import FormRequestMixin
from aristotle_mdr.fields import LowerEmailFormField


class UserInvitationForm(FormRequestMixin, forms.Form):
    email_list = forms.CharField(
        widget=forms.Textarea,
        label="User emails",
        help_text="Enter one email per line."
    )

    def clean_email_list(self):
        data = self.cleaned_data['email_list']
        emails = [e.strip() for e in data.split('\n')]

        errors = []
        for i, email in enumerate(emails):
            email = email.lower()
            if email.strip() == "":
                continue
            try:
                validate_email(email)
            except ValidationError:
                errors.append(
                    _("The email '%(email)s' on line %(line_no)d is not valid") % {"email": email, "line_no": i + 1}
                )

        if errors:
            raise ValidationError(errors)

        emails = [e.strip().lower() for e in data.split('\n') if e != ""]
        self.cleaned_data['email_list'] = "\n".join(emails)

        self.emails = emails


class ResendActivationForm(forms.Form):
    email = LowerEmailFormField(widget=forms.EmailInput(attrs={'class': 'form-control'}))


class UserRegistrationForm(forms.ModelForm):

    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput
    )
    password_confirm = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput
    )
    email = LowerEmailFormField(
        max_length=254
    )

    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password != password_confirm or not password:
            raise forms.ValidationError(_('Your password entries must match'))
        return super(UserRegistrationForm, self).clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = get_user_model()
        fields = ['short_name', 'full_name', 'email']


class UpdateAnotherUserSiteWidePermsForm(forms.Form):
    is_superuser = forms.BooleanField(
        required=False,
        label="Enable superuser permissions",
        help_text="Enable this to allow a user to see and edit all content, metadata and pages stored in the registry"
    )

    is_staff = forms.BooleanField(
        required=False,
        label="Access Django admin area",
        help_text="Enable this to allow a user to access the Django administration area"
    )
    perm_view_all_metadata = forms.BooleanField(
        required=False,
        label="Allow user to view all metadata",
        help_text="Enable this to allow a user to see all metadata stored in the registry, including those in all users sandboxes. This will also allow them to view all issues for metadata."
    )
