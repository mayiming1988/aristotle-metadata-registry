from django import forms

import aristotle_mdr.models as MDR
from aristotle_mdr.contrib.stewards.models import Collection
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.forms.creation_wizards import UserAwareFormMixin
from aristotle_mdr.forms.utils import BootstrapableMixin


class CollectionForm(BootstrapableMixin, UserAwareFormMixin, forms.ModelForm):
    metadata = forms.ModelMultipleChoiceField(
        queryset=MDR._concept.objects.all(),
        label="Included metadata", required=False,
        widget=widgets.ConceptAutocompleteSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['metadata'].queryset = MDR._concept.objects.visible(self.user)

    class Meta:
        model = Collection
        fields = ['name', 'parent_collection', 'description', 'metadata']
