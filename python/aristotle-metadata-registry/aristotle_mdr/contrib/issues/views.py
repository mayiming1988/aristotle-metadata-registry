from django.http import Http404
from django.views.generic import TemplateView

from aristotle_mdr.views.utils import SimpleItemGet
from aristotle_mdr.contrib.issues.models import Issue
from aristotle_mdr import perms
from django.contrib.auth.mixins import LoginRequiredMixin


class IssueBase(LoginRequiredMixin, SimpleItemGet):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['activetab'] = 'issues'
        context['hide_item_actions'] = True
        return context


class IssueList(IssueBase, TemplateView):

    template_name='aristotle_mdr/issues/list.html'

    def get_issues(self):
        open_issues = self.item.issues.filter(isopen=True).order_by('created')
        closed_issues = self.item.issues.filter(isopen=False).order_by('created')
        return open_issues, closed_issues

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        open_issues, closed_issues = self.get_issues()
        context.update({
            'open_issues': open_issues,
            'closed_issues': closed_issues
        })
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
        item = self.get_item(request.user)

        self.item = item
        self.issue = self.get_issue()
        if not self.issue:
            raise Http404

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
        context['own_issue'] = (self.request.user.id == self.issue.submitter.id)
        return context
