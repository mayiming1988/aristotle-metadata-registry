from django.views.generic import TemplateView

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.contrib.validators.schema.load import load_schema
from aristotle_mdr.contrib.validators import models


class RegistryValidationRuleEditView(IsSuperUserMixin, TemplateView):
    template_name='aristotle_mdr/validation/edit.html'

    def get_registry_rules(self):
        rules = models.RegistryValidationRules.objects.first()
        if rules is None:
            rules = models.RegistryValidationRules.objects.create()
        return rules

    def get_context_data(self):
        context = super().get_context_data()
        context['schema'] = load_schema()
        context['rules'] = self.get_registry_rules()
        return context
