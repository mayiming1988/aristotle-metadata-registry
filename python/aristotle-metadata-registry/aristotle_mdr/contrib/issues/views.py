from typing import Optional

from django.http import Http404
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from aristotle_mdr.views.utils import SimpleItemGet
from aristotle_mdr.contrib.issues.models import Issue
from aristotle_mdr.models import _concept
from aristotle_mdr import perms
import json
from django.contrib.auth.mixins import LoginRequiredMixin


class IssueBase(LoginRequiredMixin, SimpleItemGet):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['activetab'] = 'issues'
        context['hide_item_actions'] = True
        return context

    def get_modal_data(self, issue=None):
        """Get data for issue modal creation and editing"""
        # Get field data for proposable fields on concept
        field_data = {}
        for fname in Issue.proposable_fields:
            value = getattr(self.item, fname, '')
            field_data[fname] = value

        data = {}
        if issue:
            data['proposal_field'] = issue.proposal_field
            data['proposal_value'] = issue.proposal_value
            data['name'] = issue.name
            data['description'] = issue.description
        return {
            'fields': json.dumps(Issue.get_propose_fields()),
            'field_data': field_data,
            'initial': json.dumps(data)
        }


class IssueList(IssueBase, TemplateView):

    template_name='aristotle_mdr/issues/list.html'

    def get_issues(self):
        open_issues = self.item.issues.filter(isopen=True).order_by('created')
        closed_issues = self.item.issues.filter(isopen=False).order_by('created')
        return open_issues, closed_issues

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Fetch issues for the item
        open_issues, closed_issues = self.get_issues()
        # Update context
        context.update({
            'open_issues': open_issues,
            'closed_issues': closed_issues,
        })
        # Update context with modal data
        context.update(self.get_modal_data())
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
        context.update(self.get_modal_data(self.issue))
        return context
