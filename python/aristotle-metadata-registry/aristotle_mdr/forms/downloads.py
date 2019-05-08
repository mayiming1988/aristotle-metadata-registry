from django import forms
from aristotle_mdr.models import RegistrationAuthority, STATES


class ModelChoicePKField(forms.ModelChoiceField):
    """ Overriding the to_python so that we can pass the pk directly to the download view, without
    it (unsuccessfully) trying to JSON serialize the Registration Authority object """
    def to_python(self, value):
        if value in self.empty_values:
            return None
        return value


class DownloadOptionsForm(forms.Form):

    def __init__(self, *args, wrap_pages: bool, **kwargs):
        super().__init__(*args, **kwargs)
        # Add front page and back page options
        if wrap_pages:
            self.fields['front_page'] = forms.FileField(
                required=False,
                help_text='A front page to be added to the document. Must be in the same format as the download'
            )
            self.fields['back_page'] = forms.FileField(
                required=False,
                help_text='A back page to be added to the document. Must be in the same format as the download'
            )
        self.wrap_pages = wrap_pages

    title = forms.CharField(
        required=False,
        help_text='Optional title of the document'
    )

    include_supporting = forms.BooleanField(
        required=False,
        help_text='Include the name and definition for components of the item (e.g. the Value Domain of a Data Element)'
    )
    include_related = forms.BooleanField(
        required=False,
        help_text='Include the name and definition of all concepts implementing the item (e.g. the Data Elements using a Value Domain)'
    )

    registration_authority = ModelChoicePKField(
            queryset=RegistrationAuthority.objects.all(),
            required=False,
            help_text="Select a particular registration authority to filter the supporting items on"
        )
    registration_status = forms.ChoiceField(
        choices=STATES,
        required=False,
        help_text="Select a particular registration status to filter the supporting items on"
    )

    email_copy = forms.BooleanField(
        required=False,
        help_text='Send a copy of the download to your email address'
    )
