from django.forms import Field
from django.forms.models import ModelMultipleChoiceField
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
import aristotle_mdr.models as MDR
from aristotle_mdr.models import STATES, Status
from aristotle_mdr.utils import status_filter
from django.forms.widgets import EmailInput
from aristotle_mdr.widgets.widgets import TableCheckboxSelect, MultiTextWidget
from django.urls import reverse
from aristotle_mdr import perms


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

        extra_info = {}
        subclassed_queryset = queryset.select_subclasses()
        statuses = Status.objects.filter(concept__in=queryset, registrationAuthority=ra).select_related('concept')
        statuses = status_filter(statuses).order_by("-registrationDate", "-created")

        new_state_num = static_content['new_state']
        new_state = str(STATES[new_state_num])

        # Build a dict mapping concepts to their status data
        # So that no additional status queries need to be made
        states_dict = {}
        for status in statuses:
            state_name = str(STATES[status.state])
            reg_date = status.registrationDate
            if status.concept.id not in states_dict:
                states_dict[status.concept.id] = {
                    'name': state_name,
                    'reg_date': reg_date,
                    'state': status.state
                }

        deselections = False
        for concept in subclassed_queryset:
            url = reverse('aristotle:registrationHistory', kwargs={'iid': concept.id})

            innerdict = {}
            # Get class name
            innerdict['type'] = concept.__class__.get_verbose_name()
            innerdict['checked'] = True

            try:
                state_info = states_dict[concept.id]
            except KeyError:
                state_info = None

            if state_info:
                innerdict['old'] = {
                    'url': url,
                    'text': state_info['name'],
                    'old_reg_date': state_info['reg_date']
                }
                if state_info['state'] >= new_state_num:
                    innerdict['checked'] = False
                    deselections = True

            innerdict['perm'] = perms.user_can_change_status(user, concept)
            innerdict['new_state'] = {'url': url, 'text': new_state}

            extra_info[concept.id] = innerdict

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
