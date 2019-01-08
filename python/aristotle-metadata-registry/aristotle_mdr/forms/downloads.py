from django import forms


class DownloadOptionsForm(forms.Form):
    include_supporting = forms.BooleanField(required=False)
    email_copy = forms.BooleanField(required=False)
