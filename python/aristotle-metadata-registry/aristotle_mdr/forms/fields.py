from django.forms import Field
from django.forms.models import ModelMultipleChoiceField
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.forms.widgets import EmailInput
from aristotle_mdr.widgets.widgets import TableCheckboxSelect, MultiTextWidget
from aristotle_mdr import perms
from aristotle_mdr.utils import get_status_change_details


class ReviewChangesChoiceField(ModelMultipleChoiceField):

    def __init__(self, queryset, static_content, ra, user, **kwargs):

        extra_info, deselections = self.build_extra_info(queryset, ra, user, static_content)
        static_content.pop('new_state')  # Added this to extra with a dynamic url attached

        headers = {
            'input': '',
            'label': '',
            'old_reg_date': 'Registration Date',
            'type': '',
            'old': 'State',
            'new_state': 'State',
            'new_reg_date': 'Registration Date',
        }

        top_header = [
            {'text': 'Select', 'rowspan': 2},
            {'text': 'Name', 'rowspan': 2},
            {'text': 'Type', 'rowspan': 2},
            {'text': 'Previous', 'colspan': 2},
            {'text': 'New', 'colspan': 2}
        ]

        order = ['input', 'label', 'type', 'old', 'old_reg_date', 'new_state', 'new_reg_date']

        self.widget = TableCheckboxSelect(
            extra_info=extra_info,
            static_info=static_content,
            attrs={'tableclass': 'table'},
            headers=headers,
            top_header=top_header,
            order=order,
            deselections=deselections
        )

        super().__init__(queryset, **kwargs)

    def build_extra_info(self, queryset, ra, user, static_content):
        (extra_info, deselections) = get_status_change_details(queryset, ra, static_content['new_state'])
        for key, item in extra_info.items():
            item['checked'] = not item['has_higher_status']
            item['perm'] = perms.user_can_change_status(user, item['concept'])

        return (extra_info, deselections)


class MultipleEmailField(Field):

    def __init__(self, *args, **kwargs):
        self.widget = MultiTextWidget(
            subwidget=EmailInput,
            attrs={
                'class': 'form-control'
            }
        )
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        cleaned_values = []
        validator = EmailValidator()

        valid = True
        errors = []

        for email in value:
            if email is not '':
                validator.message = '{} is not a valid email address'.format(email)
                try:
                    validator(email)
                except ValidationError as e:
                    valid = False
                    errors.extend(e.error_list)

                cleaned_values.append(email)

        if valid:
            return cleaned_values
        else:
            raise ValidationError(errors)
