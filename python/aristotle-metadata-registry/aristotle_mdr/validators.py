import re
from aristotle_mdr import models


class BaseValidator:

    def __init__(self, rule):
        if 'name' in rule:
            self.name = rule['name']
        else:
            self.name = 'Unnamed {}'.format(rule['validator'])
        self.rule = rule

    def getName(self):
        return self.name

    def validate(self, item, ra=None):
        # To be overwritten in child
        # Should return status, message
        raise NotImplementedError


class RegexValidator(BaseValidator):

    def validate(self, item, ra=None):
        field_data = getattr(item, self.rule['field'])
        match = re.fullmatch(self.rule['regex'], field_data)
        return (match is not None), ''


class StatusValidator(BaseValidator):

    def validate(self, item, ra=None):
        if not ra:
            return False, 'Invalid rule'

        allowed_statuses = self.rule['status']
        allowed_states = []

        for status in allowed_statuses:
            state = getattr(models.STATES, status.lower(), None)
            if state is None:
                return False, 'Invalid rule'

            allowed_states.append(state)

        statuses = models.Status.objects.filter(
            concept=item._concept_ptr,
            registrationAuthority=ra,
        ).order_by(
            '-registrationDate',
            '-created'
        )

        if not statuses.exists():
            return False, 'Invalid State'

        last_status = statuses.first()
        last_state = last_status.state

        if last_state in allowed_states:
            return True, 'Valid State'
        else:
            return False, 'Invalid State'
