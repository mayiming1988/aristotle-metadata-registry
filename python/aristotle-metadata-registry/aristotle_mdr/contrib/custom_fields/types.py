from django import forms
from model_utils import Choices


# Type choices presented when creating a custom field
type_choices = Choices(
    ('int', 'Integer'),
    ('str', 'String'),
    ('html', 'Rich Text'),
    ('date', 'Date')
)


# Form field used when creating a custom value of the specified type
type_field_mapping = {
    'int': forms.IntegerField,
    'str': forms.CharField,
    'date': forms.DateField,
    'html': forms.CharField
}
