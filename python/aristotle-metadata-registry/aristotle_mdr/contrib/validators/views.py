from django.views.generic import TemplateView

from aristotle_mdr.contrib.validators.schema.load import load_schema


class ValidationRuleEditView(TemplateView):
    template_name='aristotle_mdr/validation/edit.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['schema'] = load_schema()
        return context
