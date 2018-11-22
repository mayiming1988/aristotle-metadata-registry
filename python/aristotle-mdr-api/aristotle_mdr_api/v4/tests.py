from rest_framework.test import APIClient
from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.issues import models
from aristotle_mdr.contrib.favourites.models import Tag, Favourite
from aristotle_mdr.contrib.favourites.tests import BaseFavouritesTestCase


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

    def login_user(self):
        self.client.login(
            email='testuser@example.com',
            password='testing123'
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


class TagsEndpointsTestCase(BaseAPITestCase, BaseFavouritesTestCase):

    def setUp(self):
        super().setUp()
        self.timtam = mdr_models.ObjectClass.objects.create(
            name='Tim Tam',
            definition='Chocolate covered biscuit',
            submitter=self.user
        )

    def test_tag_edit_add_tags(self):
        self.login_user()

        post_data = {
            'tags': ['very good', 'amazing']
        }

        response = self.client.post(
            reverse('api_v4:item_tags', args=[self.timtam.id]),
            post_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

        self.check_tag(self.user, self.timtam, 'very good', True)
        self.check_tag(self.user, self.timtam, 'amazing', True)

        self.check_tag_count(self.user, 2)
        self.check_favourite_count(self.user, 2)

        response_obj = response.data
        vg = self.get_tag(self.user, self.timtam, 'very good')
        am = self.get_tag(self.user, self.timtam, 'amazing')
        self.assertCountEqual(
            response_obj['tags'],
            [{'id': vg.id, 'name': 'very good'}, {'id': am.id, 'name': 'amazing'}]
        )

    def test_tag_edit_add_existing_tag(self):

        self.login_user()
        tag = Tag.objects.create(
            profile=self.user.profile,
            name='very good',
            primary=False
        )
        post_data = {
            'tags': ['very good']
        }

        response = self.client.post(
            reverse('api_v4:item_tags', args=[self.timtam.id]),
            post_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

        self.check_tag(self.user, self.timtam, 'very good', True)

        self.check_tag_count(self.user, 1)
        self.check_favourite_count(self.user, 1)

        response_obj = response.data
        vg = self.get_tag(self.user, self.timtam, 'very good')
        self.assertCountEqual(
            response_obj['tags'],
            [{'id': vg.id, 'name': 'very good'}]
        )

    def test_tag_edit_add_and_remove_tags(self):
        self.login_user()

        tag = Tag.objects.create(
            profile=self.user.profile,
            name='very good',
            primary=False
        )
        Favourite.objects.create(
            tag=tag,
            item=self.timtam,
        )

        post_data = {
            'tags': ['10/10']
        }
        response = self.client.post(
            reverse('api_v4:item_tags', args=[self.timtam.id]),
            post_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

        self.check_tag(self.user, self.timtam, 'very good', False)
        self.check_tag(self.user, self.timtam, '10/10', True)

        self.check_tag_count(self.user, 2)
        self.check_favourite_count(self.user, 1)

        response_obj = response.data
        ten = self.get_tag(self.user, self.timtam, '10/10')
        self.assertCountEqual(
            response_obj['tags'],
            [{'id': ten.id, 'name': '10/10'}]
        )

    def test_tag_edit_incorrect_data(self):
        self.login_user()

        post_data = {
            'bags': ['10/10']
        }
        response = self.client.post(
            reverse('api_v4:item_tags', args=[self.timtam.id]),
            post_data,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['Request'][0], 'Incorrect Request')


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
