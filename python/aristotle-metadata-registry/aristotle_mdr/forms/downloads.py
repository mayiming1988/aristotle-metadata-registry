from django import forms


class DownloadOptionsForm(forms.Form):

    def __init__(self, *args, wrap_pages: bool, **kwargs):
        super().__init__(*args, **kwargs)
        if wrap_pages:
            self.fields['front_page'] = forms.FileField(required=False)
            self.fields['back_page'] = forms.FileField(required=False)
        self.wrap_pages = wrap_pages

    title = forms.CharField(
        required=False,
        help_text='The title of the document'
    )
    include_supporting = forms.BooleanField(
        required=False,
        help_text='Include the name and definition for components of the item (e.g. the Value Domain of a Data Element)'
    )
    include_related = forms.BooleanField(
        required=False,
        help_text='Include the name and definition of all concepts implementing the item (e.g. the Data Elements using a Value Domain)'
    )
    email_copy = forms.BooleanField(
        required=False,
        help_text='Send a copy of the download to your email address'
    )
