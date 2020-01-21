from django import forms

import aristotle_mdr.models as MDR
from aristotle_mdr.contrib.stewards.models import Collection
from aristotle_mdr.contrib.autocomplete import widgets
from aristotle_mdr.forms.creation_wizards import UserAwareFormMixin
from aristotle_mdr.forms.utils import BootstrapableMixin
from aristotle_mdr.contrib.stewards.models import Collection


class CollectionForm(BootstrapableMixin, UserAwareFormMixin, forms.ModelForm):
    """Form for editing collections"""
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
        fields = ['name', 'description', 'metadata']


class MoveCollectionForm(BootstrapableMixin, UserAwareFormMixin, forms.ModelForm):
    """Form for moving a collection into a new collection
    i.e. changing the parent collection"""

    def __init__(self, *args, **kwargs):
        current_collection = kwargs.pop('current_collection')
        stewardship_organisation = current_collection.stewardship_organisation

        super().__init__(*args, **kwargs)

        field = self.fields['parent_collection']
        # Set queryset for validation
        field.queryset = Collection.objects.editable_when_manage_collections(
            stewardship_organisation
        ).exclude(id=current_collection.id)

        field.widget = widgets.CollectionSelect(
            steward_organisation_uuid=stewardship_organisation.uuid,
            steward_organisation_slug=stewardship_organisation.slug,
            current_collection_id=current_collection.id
        )
        field.widget.choices = field.choices

    class Meta:
        model = Collection
        fields = ['parent_collection']
