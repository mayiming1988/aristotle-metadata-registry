from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import VersionPublicationRecord
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker


class MetadataPublishForm(ModelForm):
    notes = forms.TextInput()

    class Meta:
        model = VersionPublicationRecord
        exclude = ['concept']
        widgets = {
            'public_user_publication_date': BootstrapDateTimePicker(
                options={"format": "YYYY-MM-DD HH:MM"}
            ),
            'authenticated_user_publication_date': BootstrapDateTimePicker(
                options={"format": "YYYY-MM-DD HH:MM"}
            ),
        }

    def clean(self):
        pub_date = self.cleaned_data['public_user_publication_date']
        priv_date = self.cleaned_data['authenticated_user_publication_date']

        if (pub_date and priv_date) and priv_date > pub_date:
            raise ValidationError(
                "Authenticated user publication date cannot be after public user publication date."
            )
