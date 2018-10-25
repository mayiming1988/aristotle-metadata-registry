import re


class BaseValidator:

    def __init__(self, rule):
        self.rule = rule

    def validate(self, field_data):
        # To be overwritten in child
        raise NotImplementedError


class RegexValidator(BaseValidator):

    def validate(self, field_data):
        match = re.fullmatch(self.rule, field_data)
        return (match is not None)
