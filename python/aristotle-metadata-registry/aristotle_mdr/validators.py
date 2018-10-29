import re


class BaseValidator:

    def __init__(self, rule):
        self.rule = rule

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
