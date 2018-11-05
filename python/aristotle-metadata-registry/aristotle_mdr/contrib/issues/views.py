from aristotle_mdr.views.utils import SimpleItemGet, TagsMixin
from aristotle_mdr.contrib.issues import models
from django.views.generic import TemplateView, DetailView


class IssueList(SimpleItemGet, TagsMixin, TemplateView):

    template_name='aristotle_mdr/issues/list.html'

    def get_issues(self):
        return self.item.issues.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['issues'] = self.get_issues()
        context['activetab'] = 'issues'
        return context


class IssueDisplay(DetailView):

    model=models.Issue
    template_name='aristotle_mdr/issues/display.html'
