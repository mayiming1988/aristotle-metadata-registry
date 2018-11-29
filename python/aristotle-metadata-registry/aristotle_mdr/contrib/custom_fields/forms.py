from typing import Iterable
from django import forms

from aristotle_mdr.contrib.custom_fields.types import type_field_mapping
from aristotle_mdr.contrib.custom_fields.models import CustomField


class CustomValueFormMixin:

    def __init__(self, custom_fields: Iterable[CustomField], **kwargs):
        super().__init__(**kwargs)
        self.custom_field_names = []
        for custom_field in custom_fields:
            field_class = type_field_mapping[custom_field.type]
            self.fields[custom_field.name] = field_class(
                required=False,
                label=custom_field.name,
                help_text=custom_field.help_text
            )
            self.custom_field_names.append(custom_field.name)

    @property
    def custom_fields(self):
        return [self[fname] for fname in self.custom_field_names]
