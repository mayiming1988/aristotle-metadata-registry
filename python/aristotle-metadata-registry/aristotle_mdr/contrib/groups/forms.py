from django import forms
from django.utils.translation import ugettext_lazy as _

from aristotle_mdr.fields import LowerEmailFormField


class RolesFormBase:
    def add_role_fields(self, manager, group, member=None):
        initial = {}
        if member:
            initial = {"initial": group.roles_for_user(member)}
        if manager.group_class.allows_multiple_roles:
            self.fields['role'] = forms.MultipleChoiceField(
                choices=group.roles,
                widget=forms.CheckboxSelectMultiple,
                label=_("Roles"),
                required=False,
                **initial,
            )
        else:
            self.fields['role'] = forms.ChoiceField(
                choices=group.roles,
                label=_("Role"),
                required=True,
                **initial,
            )


class MembershipUpdateForm(forms.Form, RolesFormBase):
    def __init__(self, manager, group, member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if manager.group_class.allows_multiple_roles:
            self.fields['role'] = forms.MultipleChoiceField(
                choices=group.roles,
                widget=forms.CheckboxSelectMultiple,
                label=_("Roles"),
                required=False,
                initial=self.group.roles_for_user(member),
            )
        else:
            self.fields['role'] = forms.ChoiceField(
                choices=group.roles,
                label=_("Role"),
                required=True,
                initial=group.roles_for_user(member),
            )


class UserFilterForm(forms.Form, RolesFormBase):
    user_filter = forms.CharField(required=False)

    def __init__(self, manager, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role_filter'] = forms.ChoiceField(
            choices=[("", "Any")] + group.roles,
            label=_("Role"),
            required=False,
            widget=forms.Select(attrs={'class': "form-control"})
        )
