from typing import Iterable
from django.views.generic import TemplateView

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.contrib.validators.schema.load import load_schema
from aristotle_mdr.contrib.validators import models


class ValidationRuleEditView(TemplateView):
    """Base view to be used for all validation rule editing"""

    def get_rules(self) -> Iterable[models.ValidationRules]:
        raise NotImplementedError

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['schema'] = load_schema()
        context['rules'] = self.get_rules()
        return context


class RegistryValidationRuleEditView(IsSuperUserMixin, ValidationRuleEditView):
    template_name='aristotle_mdr/validation/edit.html'

    def get_rules(self):
        rules = models.RegistryValidationRules.objects.first()
        if rules is None:
            rules = models.RegistryValidationRules.objects.create()
        return rules
