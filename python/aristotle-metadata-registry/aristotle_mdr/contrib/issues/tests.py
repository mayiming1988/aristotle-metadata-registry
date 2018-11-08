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

    def create_test_issue(self):
        return models.Issue.objects.create(
            name='Test issue',
            description='Just a test',
            item=self.item,
            submitter=self.editor
        )

    def test_issue_create(self):
        issue = self.create_test_issue()
        self.assertTrue(issue.isopen)
        self.assertIsNotNone(issue.created)

    def test_issue_display(self):
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
        self.assertEqual(issues[0].name, 'Test issue')
