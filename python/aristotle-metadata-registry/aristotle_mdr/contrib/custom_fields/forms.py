from typing import Iterable, List
from django import forms
from django.contrib.contenttypes.models import ContentType

from aristotle_mdr.contrib.custom_fields.types import type_field_mapping
from aristotle_mdr.contrib.custom_fields.models import CustomField, CustomValue
from aristotle_mdr.models import _concept
from aristotle_mdr.utils.utils import get_concept_content_types


class CustomFieldForm(forms.ModelForm):
    class Meta:
        model = CustomField
        exclude = ['order']

    def get_concept_qs(self):
        mapping = get_concept_content_types()
        ids = [ct.id for ct in mapping.values()]
        return ContentType.objects.filter(id__in=ids).order_by('model')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'allowed_model' in self.fields:
            self.fields['allowed_model'].queryset = self.get_concept_qs()
            self.fields['allowed_model'].empty_label = 'All'


class CustomFieldDeleteForm(forms.Form):

    method = forms.ChoiceField(
        choices=[
            ('migrate', 'Move values to standard slots'),
            ('delete', 'Remove all values')
        ],
        widget=forms.RadioSelect,
        initial='migrate',
    )


class CustomValueFormMixin:
    """Used with concept form"""

    custom_field_names: List[str]
    fields: dict
    cfields: dict
    cleaned_data: dict

    def __init__(self, custom_fields: Iterable[CustomField] = [], **kwargs):
        super().__init__(**kwargs)  # type: ignore
        self.cfields = {'custom_{}_{}'.format(cf.name, cf.id): cf for cf in custom_fields}
        self.custom_field_names = []
        for custom_fname, custom_field in self.cfields.items():
            field = type_field_mapping[custom_field.type]
            field_class = field['field']
            field_default_args = field.get('args', {})
            self.fields[custom_fname] = field_class(
                required=False,
                label=custom_field.name,
                help_text=custom_field.help_text,
                **field_default_args
            )
            self.custom_field_names.append(custom_fname)

    @property
    def custom_fields(self) -> List:
        return [self[fname] for fname in self.custom_field_names]  # type: ignore

    def save_custom_fields(self, concept: _concept) -> _concept:
        for fname in self.custom_field_names:
            data = self.cleaned_data[fname]
            if fname in self.cfields:
                field = self.cfields[fname]
                obj, created = CustomValue.objects.update_or_create(
                    field=field,
                    concept=concept,
                    defaults={'content': str(data)}
                )

        return concept
