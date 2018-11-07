from django.forms import ModelForm
from .models import VersionPublicationRecord
from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker
from django.forms import RadioSelect
from django import forms

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
