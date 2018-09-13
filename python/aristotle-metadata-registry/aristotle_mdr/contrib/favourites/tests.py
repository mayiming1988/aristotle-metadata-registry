from django.test import TestCase, tag
from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.favourites import models
from aristotle_mdr.utils import url_slugify_concept
from django.contrib.messages import get_messages

import json

@tag('favourites')
class FavouritesTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.timtam = mdr_models.ObjectClass.objects.create(
            name='Tim Tam',
            definition='Chocolate covered biscuit',
            submitter=self.editor
        )
        self.tastiness = mdr_models.Property.objects.create(
            name='Tastiness',
            definition='How good an item tastes',
            submitter=self.editor
        )
        self.ttt = mdr_models.DataElementConcept(
            name='Tim Tam - Tastiness',
            definition='Tim Tam - Tastiness',
            objectClass=self.timtam,
            property=self.tastiness,
            submitter=self.editor
        )

    # --- Utils ---

    def check_favourite(self, user, item, status):
        favourited = models.Favourite.objects.filter(
            item_id=item.id,
            tag__primary=True,
            tag__profile=user.profile
        ).exists()
        self.assertEqual(favourited, status)

    def check_tag(self, user, item, tag, status):

        tagged = models.Favourite.objects.filter(
            item_id=item.id,
            tag__primary=False,
            tag__profile=user.profile,
            tag__name=tag
        ).exists()
        self.assertEqual(tagged, status)

    def check_tag_count(self, user, count):
        user_tags = models.Tag.objects.filter(
            profile=user.profile
        ).count()
        self.assertEqual(user_tags, count)

    def check_favourite_count(self, user, count):
        user_favourites = models.Favourite.objects.filter(
            tag__profile=user.profile
        ).count()
        self.assertEqual(user_favourites, count)

    # --- Tests ---

    def test_toggle_favourite_function_on(self):

        self.login_editor()
        self.check_favourite(self.editor, self.timtam, False)

        self.editor.profile.toggleFavourite(self.timtam)

        self.check_favourite(self.editor, self.timtam, True)

    def test_toggle_favourite_function_off(self):

        self.login_editor()
        self.check_favourite(self.editor, self.timtam, False)

        self.editor.profile.toggleFavourite(self.timtam)

        self.check_favourite(self.editor, self.timtam, True)

        self.editor.profile.toggleFavourite(self.timtam)

        self.check_favourite(self.editor, self.timtam, False)

    def test_toggle_favourite_on_view(self):

        self.login_editor()
        self.check_favourite(self.editor, self.timtam, False)

        response = self.reverse_get(
            'aristotle_favourites:toggleFavourite',
            reverse_args=[self.timtam.id],
            status_code=302
        )
        self.assertEqual(response.url, url_slugify_concept(self.timtam))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(messages[1].message.startswith('Tim Tam added to favourites'))

        self.check_favourite(self.editor, self.timtam, True)

    def test_toggle_favourite_off_view(self):

        primtag = models.Tag.objects.create(
            profile=self.editor.profile,
            name='',
            primary=True
        )
        models.Favourite.objects.create(
            tag=primtag,
            item=self.timtam
        )

        self.login_editor()
        self.check_favourite(self.editor, self.timtam, True)

        response = self.reverse_get(
            'aristotle_favourites:toggleFavourite',
            reverse_args=[self.timtam.id],
            status_code=302
        )
        self.assertEqual(response.url, url_slugify_concept(self.timtam))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(messages[1].message.startswith('Tim Tam removed from favourites'))

        self.check_favourite(self.editor, self.timtam, False)

    def test_toggle_non_viewable(self):

        self.login_viewer()

        response = self.reverse_get(
            'aristotle_favourites:toggleFavourite',
            reverse_args=[self.timtam.id],
            status_code=403
        )

    def test_tag_edit_add_tags(self):

        self.login_editor()

        tags = ['very good', 'amazing']
        post_data = {
            'tags': json.dumps(tags)
        }

        response = self.reverse_post(
            'aristotle_favourites:edit_tags',
            post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            reverse_args=[self.timtam.id]
        )

        response_obj = json.loads(response.content)
        self.assertTrue(response_obj['success'])

        self.check_tag(self.editor, self.timtam, 'very good', True)
        self.check_tag(self.editor, self.timtam, 'amazing', True)

        self.check_tag_count(self.editor, 2)
        self.check_favourite_count(self.editor, 2)

    def test_tag_edit_add_and_remove_tags(self):

        self.login_editor()

        tag = models.Tag.objects.create(
            profile=self.editor.profile,
            name='very good',
            primary=False
        )
        models.Favourite.objects.create(
            tag=tag,
            item=self.timtam,
        )

        post_data = {
            'tags': json.dumps(['10/10'])
        }

        response = self.reverse_post(
            'aristotle_favourites:edit_tags',
            post_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            reverse_args=[self.timtam.id]
        )

        response_obj = json.loads(response.content)
        self.assertTrue(response_obj['success'])

        self.check_tag(self.editor, self.timtam, 'very good', False)
        self.check_tag(self.editor, self.timtam, '10/10', True)

        self.check_tag_count(self.editor, 2)
        self.check_favourite_count(self.editor, 1)
