from typing import Iterable, List
from django import forms
from django.contrib.contenttypes.models import ContentType

from aristotle_mdr.contrib.custom_fields.types import type_field_mapping
from aristotle_mdr.contrib.custom_fields.models import CustomField, CustomValue
from aristotle_mdr.models import _concept


class CustomFieldForm(forms.ModelForm):
    class Meta:
        model = CustomField
        exclude = ['order']

    def get_concept_qs(self):
        return ContentType.objects.filter(app_label='aristotle_mdr')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'allowed_models' in self.fields:
            self.fields['allowed_models'].queryset = self.get_concept_qs()


class CustomValueFormMixin:

    custom_field_names: List[str]
    fields: dict
    cfields: dict
    cleaned_data: dict

    def __init__(self, custom_fields: Iterable[CustomField], **kwargs):
        super().__init__(**kwargs)  # type: ignore
        self.cfields = {'custom_{}'.format(cf.name): cf for cf in custom_fields}
        self.custom_field_names = []
        for custom_field in self.cfields.values():
            field = type_field_mapping[custom_field.type]
            field_class = field['field']
            field_default_args = field.get('args', {})
            custom_fname = 'custom_{}'.format(custom_field.name)
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
