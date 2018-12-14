from django import forms


class DownloadOptionsForm(forms.Form):

    include_supporting = forms.BooleanField()
    email_copy = forms.BooleanField()
