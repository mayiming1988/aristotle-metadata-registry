from typing import Iterable
from django import forms

from aristotle_mdr.contrib.custom_fields.types import type_field_mapping
from aristotle_mdr.contrib.custom_fields.models import CustomField, CustomValue


class CustomValueFormMixin:

    def __init__(self, custom_fields: Iterable[CustomField], **kwargs):
        super().__init__(**kwargs)
        self.cfields = {'custom_{}'.format(cf.name): cf for cf in custom_fields}
        self.custom_field_names = []
        for custom_field in self.cfields.values():
            field_class = type_field_mapping[custom_field.type]
            custom_fname = 'custom_{}'.format(custom_field.name)
            self.fields[custom_fname] = field_class(
                required=False,
                label=custom_field.name,
                help_text=custom_field.help_text
            )
            self.custom_field_names.append(custom_fname)

    @property
    def custom_fields(self):
        return [self[fname] for fname in self.custom_field_names]

    def save_custom_fields(self, concept):
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
