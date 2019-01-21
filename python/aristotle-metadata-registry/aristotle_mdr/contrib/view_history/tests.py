from django.core.management import call_command
from django.urls import reverse
from django.test import TestCase

from django.utils.timezone import now
import datetime


from aristotle_mdr.contrib.view_history.models import UserViewHistory
from aristotle_mdr.models import ObjectClass
from aristotle_mdr.tests import utils
from aristotle_mdr.utils import setup_aristotle_test_environment

setup_aristotle_test_environment()


class TestViewHistory(utils.LoggedInViewPages, TestCase):
    itemType = ObjectClass

    def setUp(self):
        super().setUp()

        self.item1 = self.itemType.objects.create(
            name="Test Item 1 (visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg1,
        )
        self.item2 = self.itemType.objects.create(
            name="Test Item 2 (NOT visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg2,
        )
        self.item3 = self.itemType.objects.create(
            name="Test Item 3 (visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg1,
        )

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    def test_counts_increment(self):
        self.logout()

        self.assertEqual(self.item1.user_view_history.all().count(), 0)
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(self.item1.user_view_history.all().count(), 0)

        self.login_editor()
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(self.item1.user_view_history.all().count(), 1)
        self.assertEqual(self.editor.recently_viewed_metadata.all().count(), 1)

        self.assertEqual(self.item2.user_view_history.all().count(), 0)
        response = self.client.get(self.item2.get_absolute_url())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.item2.user_view_history.all().count(), 0)
        self.assertEqual(self.editor.recently_viewed_metadata.all().count(), 1)

    def test_history_page_works(self):
        self.login_editor()
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(self.item1.user_view_history.all().count(), 1)
        self.assertEqual(self.editor.recently_viewed_metadata.all().count(), 1)
        UserViewHistory.objects.create(
            user=self.editor,
            concept=self.item1,
            # view_date=(now() - datetime.timedelta(days=1))
        )
        self.assertEqual(self.item1.user_view_history.filter(user=self.editor).all().count(), 2)

        # Try and view item2, but cant so count doesn't change
        response = self.client.get(self.item2.get_absolute_url())
        self.assertEqual(self.item2.user_view_history.all().count(), 0)
        self.assertEqual(self.editor.recently_viewed_metadata.all().count(), 2)

        response = self.client.get(self.item3.get_absolute_url())
        self.assertEqual(self.item3.user_view_history.all().count(), 1)
        self.assertEqual(self.editor.recently_viewed_metadata.all().count(), 3)

        response = self.client.get(reverse("recently_viewed_metadata"))
        self.assertEqual(len(response.context['page']), 3)

        # Item 3 was seen most recently and shows up first
        self.assertEqual(response.context['page'][0].concept.pk, self.item3.pk)
        self.assertEqual(response.context['page'][1].concept.pk, self.item1.pk)
        self.assertEqual(response.context['page'][2].concept.pk, self.item1.pk)

    def test_counts_show_in_search(self):
        self.logout()

        # Setup
        self.login_editor()
        response = self.client.get(self.item1.get_absolute_url())
        self.assertEqual(self.item1.user_view_history.all().count(), 1)
        self.assertEqual(self.editor.recently_viewed_metadata.all().count(), 1)

        # Fake a really old one
        UserViewHistory.objects.create(
            user=self.editor,
            concept=self.item1,
            view_date="1986-04-28"
        )
        self.assertEqual(self.item1.user_view_history.filter(user=self.editor).all().count(), 2)

        response = self.client.get(reverse('aristotle:search') + "?q=visible")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page'].object_list), 2)
        self.assertContains(response, "You've viewed this item")
        self.assertContains(response, "1 time")
        self.assertContains(response, "in the last month.")

        UserViewHistory.objects.create(
            user=self.editor,
            concept=self.item1,
            view_date=(now() - datetime.timedelta(days=1))
        )
        self.assertEqual(self.item1.user_view_history.filter(user=self.editor).all().count(), 3)

        response = self.client.get(reverse('aristotle:search') + "?q=visible")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page'].object_list), 2)
        self.assertContains(response, "You've viewed this item")
        self.assertContains(response, "2 times")
        self.assertContains(response, "in the last month.")

        for i in range(4, 16):
            UserViewHistory.objects.create(
                user=self.editor,
                concept=self.item1,
                view_date=(now() - datetime.timedelta(days=i))
            )

        self.assertEqual(self.item1.user_view_history.filter(user=self.editor).all().count(), 15)

        response = self.client.get(reverse('aristotle:search') + "?q=visible")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page'].object_list), 2)
        self.assertContains(response, "You've viewed this item")
        self.assertContains(response, "many times")
        self.assertContains(response, "in the last month.")
