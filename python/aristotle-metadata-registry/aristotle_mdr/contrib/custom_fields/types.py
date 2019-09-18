from django import forms
from model_utils import Choices
from ckeditor.fields import RichTextFormField

from aristotle_mdr.widgets.bootstrap import BootstrapDateTimePicker


# Type choices presented when creating a custom field
type_choices = Choices(
    ('int', 'Integer'),
    ('str', 'Text'),
    ('html', 'Rich Text'),
    ('date', 'Date'),
    ('enum', 'Choice')
)


# Form field used when creating a custom value of the specified type
type_field_mapping = {
    'int': {
        'field': forms.IntegerField,
    },
    'str': {
        'field': forms.CharField,
        'args': {
            'widget': forms.widgets.Textarea
        }
    },
    'date': {
        'field': forms.DateField,
        'args': {
            'widget': BootstrapDateTimePicker(options={'format': 'YYYY-MM-DD'})
        }
    },
    'html': {
        'field': RichTextFormField
    },
    'enum': {
        'field': forms.ChoiceField
    }
}
