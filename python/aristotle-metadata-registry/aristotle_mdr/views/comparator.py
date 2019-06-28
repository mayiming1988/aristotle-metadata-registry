import json

from django.db.models import Model
from django.utils.functional import cached_property

from aristotle_mdr.forms import CompareConceptsForm
from aristotle_mdr.models import _concept
from reversion.models import Version

from .tools import AristotleMetadataToolView
from .versions import ConceptVersionCompareBase


class MetadataComparison(ConceptVersionCompareBase, AristotleMetadataToolView):
    template_name = 'aristotle_mdr/actions/compare/compare_items.html'

    def get_form(self):
        data = self.request.GET
        user = self.request.user
        qs = _concept.objects.visible(user)
        return CompareConceptsForm(data, user=user, qs=qs)  # A form bound to the POST data

    def get_version_jsons(self, first_version, second_version):
        return (
            json.loads(first_version.serialized_data),
            json.loads(second_version.serialized_data),
            False
        )

    @cached_property
    def has_same_base_model(self):
        concept_1 = self.get_version_1_concept()
        concept_2 = self.get_version_2_concept()

        return concept_1._meta.model == concept_2._meta.model

    def get_subitem_key(self, subitem_model):
        field_names = [f.name for f in subitem_model._meta.get_fields()]
        if 'order' in field_names:
            key = 'order'
        elif 'field' in field_names and self.has_same_base_model:
            key = 'field'
        elif 'field' in field_names and not self.has_same_base_model:
            key = 'name'
        else:
            key = 'id'
        return key

    def get_model(self, concept) -> Model:
        if self.has_same_base_model:
            return concept.item._meta.model

        return _concept

    def get_version_1_concept(self):
        form = self.get_form()
        if form.is_valid():
            # Get items from form
            return form.cleaned_data['item_a'].item
        return None

    def get_version_2_concept(self):
        form = self.get_form()
        if form.is_valid():
            # Get items from form
            return form.cleaned_data['item_b'].item
        return None

    def get_compare_versions(self):
        concept_1 = self.get_version_1_concept()
        concept_2 = self.get_version_2_concept()

        if not concept_1 or not concept_2:
            return None, None

        version_1 = Version.objects.get_for_object(concept_1).order_by('-revision__date_created').first().pk
        version_2 = Version.objects.get_for_object(concept_2).order_by('-revision__date_created').first().pk

        return (version_1, version_2)

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)

        if self.get_version_1_concept() is None and self.get_version_2_concept() is None:
            # Not all concepts selected
            self.context['form']  = self.get_form()
            return self.context

        self.context.update({
            "form": self.get_form(),
            "has_same_base_model": self.has_same_base_model,
            "item_a": self.get_version_1_concept(),
            "item_b": self.get_version_2_concept(),
        })

        return self.context
