from django.forms import Field
from django.forms import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.forms.widgets import EmailInput
from aristotle_mdr.widgets.widgets import TableCheckboxSelect, MultiTextWidget
from aristotle_mdr import perms
from aristotle_mdr.utils import get_status_change_details


class ReviewChangesChoiceField(models.ModelMultipleChoiceField):

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
            item['perm'] = perms.user_can_add_status(user, item['concept'])

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
            if email != '':
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


class ForbiddenAllowedModelMultipleChoiceField(models.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.validate_queryset = kwargs.pop('validate_queryset')
        super().__init__(*args, **kwargs)

    def _check_values(self, value):
        """
        Given a list of possible PK values, returns a QuerySet of the
        corresponding objects. Skips values if they are not in the queryset.
        This allows us to force a limited selection to the client, while
        ignoring certain additional values if given. However, this means
        *extra checking must be done* to limit over exposure and invalid
        data.
        """
        from django.core.exceptions import ValidationError
        from django.utils.encoding import force_text

        key = self.to_field_name or 'pk'
        # deduplicate given values to avoid creating many querysets or
        # requiring the database backend deduplicate efficiently.
        try:
            value = frozenset(value)
        except TypeError:
            # list of lists isn't hashable, for example
            raise ValidationError(
                self.error_messages['list'],
                code='list',
            )
        for pk in value:
            try:
                self.validate_queryset.filter(**{key: pk})
            except (ValueError, TypeError):
                raise ValidationError(
                    self.error_messages['invalid_pk_value'],
                    code='invalid_pk_value',
                    params={'pk': pk},
                )
        qs = self.validate_queryset.filter(**{'%s__in' % key: value})
        pks = set(force_text(getattr(o, key)) for o in qs)
        for val in value:
            if force_text(val) not in pks:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )
        return qs
