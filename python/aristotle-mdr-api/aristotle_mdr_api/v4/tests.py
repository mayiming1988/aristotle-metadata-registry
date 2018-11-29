from rest_framework.test import APIClient
from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.issues import models
from aristotle_mdr.contrib.custom_fields import models as cf_models


class BaseAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.um = get_user_model()
        self.user = self.um.objects.create_user(
            email='testuser@example.com',
            password='testing123'
        )
        self.other_user = self.um.objects.create_user(
            email='anothertestuser@example.com',
            password='1234'
        )
        self.wg = mdr_models.Workgroup.objects.create(
            name='Best Working Group'
        )
        self.su = self.um.objects.create_user(
            email='super@example.com',
            password='1234'
        )

    def login_user(self):
        self.client.login(
            email='testuser@example.com',
            password='testing123'
        )

    def login_superuser(self):
        self.client.login(
            email='super@example.com',
            password='1234'
        )

    def login_other_user(self):
        self.client.login(
            email=self.other_user.email,
            password='1234'
        )

    def create_test_issue(self, user=None):
        submitter = user or self.user
        return models.Issue.objects.create(
            name='Many problem',
            description='many',
            item=self.item,
            submitter=submitter,
        )


class IssueEndpointsTestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='API Request',
            definition='A request to an api',
            submitter=self.user
        )

    def post_issue(self, item):
        response = self.client.post(
            reverse('api_v4:issues_create'),
            {
                'name': 'Test issue',
                'description': 'Just a test one',
                'item': item.pk,
            },
            format='json'
        )
        return response

    def test_create_issue_own_item(self):

        self.login_user()
        response = self.post_issue(self.item)

        self.assertEqual(response.status_code, 201)

    def test_create_issue_non_owned_item(self):

        self.login_user()
        item = mdr_models.ObjectClass.objects.create(
            name='New API Request',
            definition='Very new'
        )

        response = self.post_issue(item)
        self.assertEqual(response.status_code, 400)
        # Make sure error returned for item
        self.assertTrue('item' in response.data)

    @tag('issue_comment')
    def test_create_issue_comment(self):

        self.login_user()
        issue = self.create_test_issue()

        response = self.client.post(
            reverse('api_v4:issue_comment'),
            {
                'body': 'Test comment',
                'issue': issue.id
            },
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        comments = issue.comments.all()
        self.assertEqual(len(comments), 1)

    @tag('issue_comments')
    def test_cant_comment_non_viewable_issue(self):
        issue = self.create_test_issue()

        self.login_other_user()
        response = self.client.post(
            reverse('api_v4:issue_comment'),
            {
                'body': 'Test comment',
                'issue': issue.id
            },
            format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue('issue' in response.data)

    @tag('update_and_comment')
    def test_close_with_comment(self):
        issue = self.create_test_issue()

        self.login_user()
        response = self.client.post(
            reverse('api_v4:issue_update_and_comment', args=[issue.pk]),
            {
                'isopen': False,
                'comment': {
                    'body': 'Not an issue'
                }
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('issue' in response.data)
        self.assertTrue('comment' in response.data)
        self.assertFalse(response.data['issue']['isopen'])

        issue = models.Issue.objects.get(pk=issue.pk)
        self.assertFalse(issue.isopen)
        self.assertEqual(issue.comments.count(), 1)

        issuecomment = issue.comments.first()
        self.assertEqual(issuecomment.body, 'Not an issue')
        self.assertEqual(issuecomment.author, self.user)

    @tag('update_and_comment')
    def test_close_without_comment(self):
        issue = self.create_test_issue()

        self.login_user()
        response = self.client.post(
            reverse('api_v4:issue_update_and_comment', args=[issue.pk]),
            {
                'isopen': False,
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('issue' in response.data)
        self.assertFalse('comment' in response.data)
        self.assertFalse(response.data['issue']['isopen'])

        issue = models.Issue.objects.get(pk=issue.pk)
        self.assertFalse(issue.isopen)
        self.assertEqual(issue.comments.count(), 0)


class CustomFieldsTestCase(BaseAPITestCase):

    def create_test_fields(self):
        cf_models.CustomField.objects.create(
            name='Spiciness',
            type='int',
            help_text='The Spiciness'
        )
        cf_models.CustomField.objects.create(
            name='Blandness',
            type='int',
            help_text='The Blandness'
        )

    def test_multiple_create(self):
        self.login_superuser()
        postdata = [
            {'id': 1, 'name': 'Spiciness', 'type': 'int', 'help_text': 'The Spiciness'},
            {'id': 2, 'name': 'Blandness', 'type': 'int', 'help_text': 'The Blandness'}
        ]

        response = self.client.post(
            reverse('api_v4:custom_field_list'),
            postdata,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cf_models.CustomField.objects.count(), 2)
        self.assertEqual(cf_models.CustomField.objects.get(id=1).name, 'Spiciness')
        self.assertEqual(cf_models.CustomField.objects.get(id=2).name, 'Blandness')

    def test_multiple_update(self):
        self.create_test_fields()
        self.login_superuser()

        postdata = [
            {'id': 1, 'name': 'Spic', 'type': 'int', 'help_text': 'The Spiciness'},
            {'id': 2, 'name': 'Bland', 'type': 'int', 'help_text': 'The Blandness'}
        ]

        response = self.client.post(
            reverse('api_v4:custom_field_list'),
            postdata,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cf_models.CustomField.objects.count(), 2)
        self.assertEqual(cf_models.CustomField.objects.get(id=1).name, 'Spic')
        self.assertEqual(cf_models.CustomField.objects.get(id=2).name, 'Bland')

    def test_multiple_delete(self):
        self.create_test_fields()
        self.login_superuser()

        postdata = [
            {'id': 1, 'name': 'Spiciness', 'type': 'int', 'help_text': 'The Spiciness'},
        ]

        response = self.client.post(
            reverse('api_v4:custom_field_list'),
            postdata,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cf_models.CustomField.objects.count(), 1)
        self.assertEqual(cf_models.CustomField.objects.get(id=1).name, 'Spiciness')


@tag('perms')
class PermsTestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='Brand new item',
            definition='Great'
        )
        self.issue = models.Issue.objects.create(
            name='Many problem',
            description='many',
            item=self.item,
            submitter=self.user
        )

    def post_issue_close(self, issue):
        return self.client.post(
            reverse('api_v4:issue_update_and_comment', args=[issue.pk]),
            {
                'isopen': False,
            },
            format='json'
        )

    def test_get_issue_allowed(self):
        self.item.submitter = self.user
        self.item.save()

        self.login_user()
        response = self.client.get(
            reverse('api_v4:issues', args=[self.issue.pk]),
        )
        self.assertEqual(response.status_code, 200)

    def test_get_issue_not_allowed(self):

        self.login_other_user()
        response = self.client.get(
            reverse('api_v4:issues', args=[self.issue.pk]),
        )
        self.assertEqual(response.status_code, 403)

    def test_close_issue_as_item_viewer(self):
        self.wg.viewers.add(self.other_user)
        self.item.workgroup = self.wg
        self.item.save()

        issue = self.create_test_issue()

        self.login_other_user()
        response = self.post_issue_close(issue)
        self.assertEqual(response.status_code, 403)

    def test_close_issue_as_item_editor(self):
        self.wg.submitters.add(self.other_user)
        self.item.workgroup = self.wg
        self.item.save()

        issue = self.create_test_issue()

        self.login_other_user()
        response = self.post_issue_close(issue)
        self.assertEqual(response.status_code, 200)

    def test_can_always_close_own_issue(self):
        issue = self.create_test_issue(self.other_user)

        self.login_other_user()
        response = self.post_issue_close(issue)
        self.assertEqual(response.status_code, 200)
