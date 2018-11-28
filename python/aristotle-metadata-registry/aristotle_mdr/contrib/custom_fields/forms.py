from django import forms

from aristotle_mdr.contrib.custom_fields.types import type_field_mapping


class CustomValueForm(forms.Form):

    def __init__(self, custom_field, **kwargs):
        field_class = type_field_mapping[custom_field.name]
        self.fields[custom_field.name] = field_class()
