from django.test import TestCase, tag
from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.issues import models


class IssueTests(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='Test Item',
            definition='Just a test item',
            workgroup=self.wg1
        )

    def create_test_issue(self, name='Test Issue'):
        return models.Issue.objects.create(
            name=name,
            description='Just a test',
            item=self.item,
            submitter=self.editor
        )

    def test_issue_create(self):
        issue = self.create_test_issue()
        self.assertTrue(issue.isopen)
        self.assertIsNotNone(issue.created)

    def test_issue_displays(self):
        issue = self.create_test_issue()
        self.login_viewer()
        response = self.reverse_get(
            'aristotle_issues:item_issues',
            reverse_args=[self.item.id],
            status_code=200
        )
        self.assertEqual(response.context['activetab'], 'issues')

        issues = response.context['issues']
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].name, 'Test Issue')

    def test_issues_list_open_closed(self):
        openis = self.create_test_issue()
        closedis = self.create_test_issue()
        closedis.isopen = False
        closedis.save()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle_issues:item_issues',
            reverse_args=[self.item.id],
            status_code=200
        )
        context = response.context

        self.assertEqual(len(context['open_issues']), 1)
        self.assertEqual(len(context['closed_issues']), 1)

        self.assertEqual(context['open_issues'][0].id, openis.id)
        self.assertEqual(context['closed_issues'][0].id, closedis.id)

    def test_own_issue_true_on_own_issue(self):
        issue = self.create_test_issue()
        self.login_editor()

        response = self.reverse_get(
            'aristotle_issues:issue',
            reverse_args=[self.item.id, issue.pk],
            status_code=200
        )

        self.assertTrue(response.context['own_issue'])

    def test_own_issue_false_on_othes_issue(self):
        issue = self.create_test_issue()
        self.login_viewer()

        response = self.reverse_get(
            'aristotle_issues:issue',
            reverse_args=[self.item.id, issue.pk],
            status_code=200
        )

        self.assertFalse(response.context['own_issue'])
