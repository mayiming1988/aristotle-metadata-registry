import re


class BaseValidator:

    def __init__(self, rule):
        if 'name' in rule:
            self.name = rule['name']
        else:
            self.name = 'Unnamed {}'.format(rule['validator'])
        self.rule = rule

    def getName(self):
        return self.name

    def validate(self, item):
        # To be overwritten in child
        raise NotImplementedError


class RegexValidator(BaseValidator):

    def validate(self, item):
        field_data = getattr(item, self.rule['field'])
        match = re.fullmatch(self.rule['regex'], field_data)
        return (match is not None), ''


class StatusValidator(BaseValidator):

    def validate(self, item):
        return True, ''
