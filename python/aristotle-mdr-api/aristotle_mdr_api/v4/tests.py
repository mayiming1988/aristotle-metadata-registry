from rest_framework.test import APIClient
from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth import get_user_model

from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.issues import models
from aristotle_mdr.contrib.custom_fields import models as cf_models
from aristotle_mdr.contrib.favourites.models import Tag, Favourite
from aristotle_mdr.contrib.favourites.tests import BaseFavouritesTestCase
from aristotle_mdr_api.token_auth.models import AristotleToken


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
            password='1234',
            is_superuser=True
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


class ConceptAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='Test Concept',
            definition='Concept Definition',
            submitter=self.user
        )
        self.concept = self.item._concept_ptr

    def test_get_concept(self):
        self.login_user()
        response = self.client.get(
            reverse('api_v4:item', args=[self.concept.id]),
        )
        self.assertEqual(response.status_code, 200)


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
            reverse('api_v4:issues:create'),
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
            reverse('api_v4:issues:comment'),
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
            reverse('api_v4:issues:comment'),
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
            reverse('api_v4:issues:update_and_comment', args=[issue.pk]),
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
            reverse('api_v4:issues:update_and_comment', args=[issue.pk]),
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
        cf1 = cf_models.CustomField.objects.create(
            order=1,
            name='Spiciness',
            type='int',
            help_text='The Spiciness'
        )
        cf2 = cf_models.CustomField.objects.create(
            order=2,
            name='Blandness',
            type='int',
            help_text='The Blandness'
        )
        return [cf1.id, cf2.id]

    def test_list_custom_fields(self):
        self.create_test_fields()
        self.login_superuser()

        response = self.client.get(
            reverse('api_v4:custom_field_list'),
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 2)

    def test_multiple_create(self):
        self.login_superuser()
        postdata = [
            {'order': 1, 'name': 'Spiciness', 'type': 'int', 'help_text': 'The Spiciness'},
            {'order': 2, 'name': 'Blandness', 'type': 'int', 'help_text': 'The Blandness'}
        ]

        response = self.client.post(
            reverse('api_v4:custom_field_list'),
            postdata,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cf_models.CustomField.objects.count(), 2)
        self.assertEqual(cf_models.CustomField.objects.filter(name='Spiciness').count(), 1)
        self.assertEqual(cf_models.CustomField.objects.filter(name='Blandness').count(), 1)

    def test_multiple_update(self):
        ids = self.create_test_fields()
        self.login_superuser()

        postdata = [
            {'id': ids[0], 'order': 1, 'name': 'Spic', 'type': 'int', 'help_text': 'The Spiciness'},
            {'id': ids[1], 'order': 2, 'name': 'Bland', 'type': 'int', 'help_text': 'The Blandness'}
        ]

        response = self.client.post(
            reverse('api_v4:custom_field_list'),
            postdata,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cf_models.CustomField.objects.count(), 2)
        self.assertEqual(cf_models.CustomField.objects.filter(name='Spic').count(), 1)
        self.assertEqual(cf_models.CustomField.objects.filter(name='Bland').count(), 1)

    def test_multiple_delete_does_not_work(self):
        ids = self.create_test_fields()
        self.login_superuser()

        postdata = [
            {'id': ids[0], 'order': 1, 'name': 'Spiciness', 'type': 'int', 'help_text': 'The Spiciness'},
        ]

        response = self.client.post(
            reverse('api_v4:custom_field_list'),
            postdata,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cf_models.CustomField.objects.count(), 2)


class TagsEndpointsTestCase(BaseAPITestCase, BaseFavouritesTestCase):

    def setUp(self):
        super().setUp()
        self.timtam = mdr_models.ObjectClass.objects.create(
            name='Tim Tam',
            definition='Chocolate covered biscuit',
            submitter=self.user
        )

    @tag('newview')
    def test_tag_edit_add_tags(self):
        self.login_user()

        post_data = {
            'tags': [{'name': 'very good'}, {'name': 'amazing'}],
        }

        response = self.client.put(
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

        sorted_tags = sorted(response_obj['tags'], key=lambda i: i['name'])
        self.assertEqual(len(sorted_tags), 2)
        self.assertEqual(sorted_tags[1]['id'], vg.tag.id)
        self.assertEqual(sorted_tags[1]['name'], 'very good')
        self.assertEqual(sorted_tags[0]['id'], am.tag.id)
        self.assertEqual(sorted_tags[0]['name'], 'amazing')

    def test_tag_edit_add_existing_tag(self):

        self.login_user()
        tag = Tag.objects.create(
            profile=self.user.profile,
            name='very good',
            primary=False
        )
        post_data = {
            'tags': [{'name': 'very good'}]
        }

        response = self.client.put(
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
        self.assertEqual(len(response_obj['tags']), 1)
        self.assertEqual(response_obj['tags'][0]['id'], vg.tag.id)
        self.assertEqual(response_obj['tags'][0]['name'], 'very good')

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
            'tags': [{'name': '10/10'}]
        }
        response = self.client.put(
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
        self.assertEqual(len(response_obj['tags']), 1)
        self.assertEqual(response_obj['tags'][0]['id'], ten.tag.id)
        self.assertEqual(response_obj['tags'][0]['name'], '10/10')

    def test_tag_edit_incorrect_data(self):
        self.login_user()

        post_data = {
            'tags': [{'game': '10/10'}]
        }
        response = self.client.put(
            reverse('api_v4:item_tags', args=[self.timtam.id]),
            post_data,
            format='json'
        )

        self.assertEqual(response.status_code, 400)

    def test_tag_view_patch(self):
        tag = Tag.objects.create(
            name='mytag',
            description='Yeet',
            profile=self.user.profile
        )

        self.login_user()
        response = self.client.patch(
            reverse('api_v4:tags', args=[tag.id]),
            {'description': 'no'},
            format='json'
        )
        self.assertEqual(response.status_code, 200)

        tag = Tag.objects.get(id=tag.id)
        self.assertEqual(tag.description, 'no')

    def test_tag_delete(self):
        tag = Tag.objects.create(
            name='mytag',
            description='Yeet',
            profile=self.user.profile
        )

        self.login_user()
        response = self.client.delete(
            reverse('api_v4:tags', args=[tag.id]),
            {'description': 'no'},
            format='json'
        )
        self.assertEqual(response.status_code, 204)

        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_request_invalid_item(self):
        self.login_user()
        response = self.client.delete(
            reverse('api_v4:tags', args=[99]),
            {'description': 'no'},
            format='json'
        )
        self.assertEqual(response.status_code, 404)


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
            reverse('api_v4:issues:update_and_comment', args=[issue.pk]),
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
            reverse('api_v4:issues:issue', args=[self.issue.pk]),
        )
        self.assertEqual(response.status_code, 200)

    def test_get_issue_not_allowed(self):

        self.login_other_user()
        response = self.client.get(
            reverse('api_v4:issues:issue', args=[self.issue.pk]),
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

    def test_item_tag_edit_perms(self):
        oc = mdr_models.ObjectClass.objects.create(
            name='Wow',
            definition='wow',
            submitter=self.other_user
        )

        self.login_user()
        response = self.client.put(
            reverse('api_v4:item_tags', args=[oc.id]),
            {'tags': [{'name': 'wowee'}]},
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_tag_view_perms(self):
        tag = Tag.objects.create(
            name='mytag',
            description='Yeet',
            profile=self.other_user.profile
        )

        self.login_user()
        response = self.client.patch(
            reverse('api_v4:tags', args=[tag.id]),
            {'description': 'no'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_tag_delete_perms(self):
        tag = Tag.objects.create(
            name='mytag',
            description='Yeet',
            profile=self.other_user.profile
        )

        self.login_user()
        response = self.client.delete(
            reverse('api_v4:tags', args=[tag.id]),
            {'description': 'no'},
            format='json'
        )
        self.assertEqual(response.status_code, 403)

        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def create_token(self, permissions):
        token = AristotleToken.objects.create(
            name='MyToken',
            key='abc',
            user=self.user,
            permissions=permissions
        )

    def query_item_with_token(self, permissions, status_code):
        """Used in the following 2 tests"""
        self.item.submitter = self.user
        self.item.save()
        self.create_token(permissions)
        self.client.credentials(HTTP_AUTHORIZATION='Token abc')
        response = self.client.get(reverse('api_v4:item', args=[self.item.id]))
        self.assertEqual(response.status_code, status_code)

    def test_query_item_with_token_correct_perms(self):
        # Query with meteadata read, expect 200
        self.query_item_with_token({'metadata': {'read': True}}, 200)

    def test_query_item_with_token_incorrect_perms(self):
        # Query without metadata read, expect 403
        self.query_item_with_token({'metadata': {'read': False}}, 403)

    def test_query_unviewable_item_with_token(self):
        # Query on item not visible to user, expect 403
        self.create_token({'metadata': {'read': True}})
        self.client.credentials(HTTP_AUTHORIZATION='Token abc')
        response = self.client.get(reverse('api_v4:item', args=[self.item.id]))
        self.assertEqual(response.status_code, 403)
