from django import forms

import aristotle_mdr.models as MDR
from aristotle_mdr.contrib.stewards.models import Collection
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.forms.creation_wizards import UserAwareFormMixin
from aristotle_mdr.forms.utils import BootstrapableMixin


class CollectionForm(BootstrapableMixin, UserAwareFormMixin, forms.ModelForm):
    """Form for editing collections"""
    metadata = forms.ModelMultipleChoiceField(
        queryset=MDR._concept.objects.all(),
        label="Included metadata", required=False,
        widget=widgets.ConceptAutocompleteSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        current_collection = kwargs.pop('current_collection', None)

        super().__init__(*args, **kwargs)

        self.fields['metadata'].queryset = MDR._concept.objects.visible(self.user)
        if 'parent_collection' in self.fields:
            # Get visible collections
            collection_qs = Collection.objects.visible(self.user)
            # Exclude current collection if provided
            if current_collection:
                collection_qs = collection_qs.exclude(id=current_collection.id)

            self.fields['parent_collection'].queryset = collection_qs

    class Meta:
        model = Collection
        fields = ['name', 'parent_collection', 'description', 'metadata']


class CreateCollectionForm(CollectionForm):
    """Form for creating collections
    Does not have field for parent_collection
    since this comes from which create button is used"""

    class Meta:
        model = Collection
        fields = ['name', 'description', 'metadata']
