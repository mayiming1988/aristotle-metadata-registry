from django.http import HttpResponseNotFound
from django.views.generic import TemplateView, DetailView

from aristotle_mdr.views.utils import SimpleItemGet, TagsMixin
from aristotle_mdr.contrib.issues.models import Issue
from aristotle_mdr import perms


class IssueBase(SimpleItemGet):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['activetab'] = 'issues'
        context['hide_item_actions'] = True
        return context


class IssueList(IssueBase, TemplateView):

    template_name='aristotle_mdr/issues/list.html'

    def get_issues(self):
        return self.item.issues.all().order_by('created')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['issues'] = self.get_issues()
        return context


class IssueDisplay(IssueBase, TemplateView):

    template_name='aristotle_mdr/issues/display.html'

    def get_issue(self):
        try:
            issue = Issue.objects.get(
                pk=self.kwargs['pk'],
                item=self.item
            )
        except Issue.DoesNotExist:
            issue = None

        return issue

    def get(self, request, *args, **kwargs):
        item, code = self.get_item(request.user)
        if not item:
            return HttpResponse(status_code=code)

        self.item = item
        self.issue = self.get_issue()
        if not self.issue:
            return HttpResponseNotFound()

        return super(IssueBase, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] = self.issue
        context['comments'] = self.issue.comments.select_related(
            'author__profile'
        ).all().order_by('created')
        context['can_open_close'] = perms.user_can(
            self.request.user,
            self.issue,
            'can_alter_open'
        )
        return context
