from django import forms


class DownloadOptionsForm(forms.Form):

    def __init__(self, *args, wrap_pages: bool, **kwargs):
        super().__init__(*args, **kwargs)
        if wrap_pages:
            self.fields['front_page'] = forms.FileField(required=False)
            self.fields['back_page'] = forms.FileField(required=False)

    include_supporting = forms.BooleanField(required=False)
    email_copy = forms.BooleanField(required=False)
