from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db.models.query import QuerySet
from django.db.models import Count

from aristotle_mdr import models as MDR
from aristotle_mdr.forms.creation_wizards import UserAwareForm
from aristotle_mdr.contrib.links.models import Relation
from aristotle_mdr.contrib.autocomplete import widgets
import logging

logger = logging.getLogger(__name__)


class LinkEndEditorBase(UserAwareForm, forms.Form):
    def __init__(self, roles, *args, **kwargs):
        self.roles = roles
        super().__init__(*args, **kwargs)
        for role in self.roles:
            if role.multiplicity == 1:
                self.fields['role_' + str(role.pk)] = forms.ModelChoiceField(
                    queryset=MDR._concept.objects.all().visible(self.user),
                    label=role.name,
                    widget=widgets.ConceptAutocompleteSelect(model=MDR._concept),
                )
            else:
                self.fields['role_' + str(role.pk)] = forms.ModelMultipleChoiceField(
                    queryset=MDR._concept.objects.all().visible(self.user),
                    label=role.name,
                    widget=widgets.ConceptAutocompleteSelectMultiple(model=MDR._concept),
                )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)
        for role in self.roles:
            field_name = 'role_' + str(role.pk)
            d = cleaned_data.get(field_name)
            if role.multiplicity is not None and d is not None and 1 < role.multiplicity < len(d):
                msg = _("Only %s  metadata items are valid for the role '%s'" % (role.multiplicity, role.name))
                self.add_error(field_name, msg)

        root_item_present = False
        for field, data in cleaned_data.items():
            if field.startswith('role_'):
                if isinstance(data, QuerySet):
                    # If data is queryset (non 1 multiplicity)
                    if self.root_item in data:
                        root_item_present = True
                        break
                else:
                    # If data is a model
                    if data == self.root_item:
                        root_item_present = True
                        break

        if not root_item_present:
            error_msg = "The metadata item '{}' must be one be included in at least one role in this link".format(self.root_item.name)
            self.add_error(None, error_msg)


class LinkEndEditor(LinkEndEditorBase):
    def __init__(self, link, roles, *args, **kwargs):
        super().__init__(roles, *args, **kwargs)
        self.root_item = link.root_item
        for role in self.roles:
            if role.multiplicity == 1:
                try:
                    concept = MDR._concept.objects.get(
                        linkend__link=link, linkend__role=role
                    )
                except (MDR._concept.DoesNotExist, MDR._concept.MultipleObjectsReturned):
                    concept = None

                if concept:
                    self.fields['role_' + str(role.pk)].initial = concept

            else:
                self.fields['role_' + str(role.pk)].initial = MDR._concept.objects.filter(
                    linkend__link=link, linkend__role=role
                )


class AddLink_SelectRelation_0(UserAwareForm, forms.Form):
    relation = forms.ModelChoiceField(
        queryset=Relation.objects.none(),
        widget=widgets.RelationAutocompleteSelect()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict to only relations with roles, queryset is used to verify entry
        qs = Relation.objects.all().visible(self.user).annotate(num_roles=Count('relationrole'))
        qs = qs.filter(num_roles__gt=0)
        self.fields['relation'].queryset = qs


class AddLink_SelectConcepts_1(LinkEndEditorBase):
    def __init__(self, *args, **kwargs):
        if 'root_item' in kwargs:
            self.root_item = kwargs.pop('root_item')
        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        cleaned_data = self.cleaned_data

        root_item_present = False
        for field, data in cleaned_data.items():
            if field.startswith('role_'):
                if isinstance(data, QuerySet):
                    # If data is queryset (non 1 multiplicity)
                    if self.root_item in data:
                        root_item_present = True
                        break
                else:
                    # If data is a model
                    if data == self.root_item:
                        root_item_present = True
                        break

        if not root_item_present:
            error_msg = '{} Must be one of the attached concepts'.format(self.root_item.name)
            self.add_error(None, error_msg)
