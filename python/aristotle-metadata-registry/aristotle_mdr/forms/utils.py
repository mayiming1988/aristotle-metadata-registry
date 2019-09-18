from django import forms

from aristotle_mdr import models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareForm, UserAwareFormMixin


class FormRequestMixin(object):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)


class RegistrationAuthorityMixin(object):
    def set_registration_authority_field(self, field_name, qs=None):
        if qs is None:
            qs = MDR.RegistrationAuthority.objects.filter(active=MDR.RA_ACTIVE_CHOICES.active)

        ras = [(ra.id, ra.name) for ra in qs]
        self.fields[field_name].queryset = qs
        self.fields[field_name].choices = ras


class BootstrapableMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class StewardOrganisationRestrictedChoicesForm(BootstrapableMixin, UserAwareFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from aristotle_mdr.models import StewardOrganisation, StewardOrganisationMembership
        qs_kwargs = {}
        if not self.user.is_superuser:
            qs_kwargs.update({
                "members__user": self.user,
                "members__role": StewardOrganisation.roles.admin,
            })
        self.fields["stewardship_organisation"].widget = forms.Select(attrs={'class': 'form-control'})
        self.fields["stewardship_organisation"].queryset = StewardOrganisation.objects.visible(self.user).filter(**qs_kwargs)
