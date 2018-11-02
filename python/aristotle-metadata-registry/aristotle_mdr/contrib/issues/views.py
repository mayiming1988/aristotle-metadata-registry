from aristotle_mdr.views.utils import SimpleItemGet, TagsMixin
from django.views.generic import TemplateView


class IssueDisplay(SimpleItemGet, TagsMixin, TemplateView):

    template_name='aristotle_mdr/issues/display.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['hide_help'] = True
        context['hide_admin_edit'] = True
        return context
