from django.test import tag
from django.urls import reverse

from aristotle_mdr import perms
from aristotle_mdr import models as mdr_models
from aristotle_mdr_api.v4.tests import BaseAPITestCase
from aristotle_mdr.contrib.favourites.tests import BaseFavouritesTestCase
from aristotle_mdr.contrib.favourites.models import Tag


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

    def test_tag_item_cant_edit(self):
        """Test that a user is allowed to tag an item they cannot edit"""
        item = mdr_models.ObjectClass.objects.create(
            name='Lammington',
            definition='Coconut on a cake',
            workgroup=self.wg
        )
        self.wg.giveRoleToUser('viewer', self.user)

        self.assertTrue(perms.user_can_view(self.user, item))
        self.assertFalse(perms.user_can_edit(self.user, item))

        post_data = {
            'tags': [{'name': 'mytag'}]
        }
        self.login_user()
        response = self.client.put(
            reverse('api_v4:item_tags', args=[item.id]),
            post_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

        self.assertTrue(Tag.objects.filter(name='mytag').exists())

    def test_cant_tag_non_viewable_item(self):
        item = mdr_models.ObjectClass.objects.create(
            name='Lammington',
            definition='Coconut on a cake',
            submitter=self.other_user
        )
        self.assertFalse(perms.user_can_view(self.user, item))

        post_data = {
            'tags': [{'name': 'mytag'}]
        }
        self.login_user()
        response = self.client.put(
            reverse('api_v4:item_tags', args=[item.id]),
            post_data,
            format='json'
        )
        self.assertEqual(response.status_code, 403)
