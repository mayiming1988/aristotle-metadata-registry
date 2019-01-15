from django.test import TestCase

from aristotle_mdr.models import ObjectClass
from django.urls import reverse

from aristotle_mdr.tests.main.test_bulk_actions import BulkActionsTest
from aristotle_mdr import models
from aristotle_mdr.utils import setup_aristotle_test_environment
from aristotle_mdr.tests.apps.text_download_test.downloader import TestTextDownloader
from aristotle_mdr.tests.utils import store_taskresult, get_download_result

from mock import patch

setup_aristotle_test_environment()


class TestBulkActions(BulkActionsTest, TestCase):
    def setUp(self):
        super().setUp()
        self.item = ObjectClass.objects.create(
            name="Test Object",
            workgroup=self.wg1,
        )

    def test_incomplete_action_exists(self):
        self.login_superuser()
        response = self.client.get(reverse('browse_concepts', args=['aristotle_mdr', 'objectclass']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incomplete action')

class TestDeleteBulkAction(BulkActionsTest, TestCase):

    def test_delete_by_superuser(self):
        self.login_superuser()

        self.assertTrue(self.su.is_staff)

        num_items = ObjectClass.objects.count()
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
            }
        )
        self.assertContains(response, 'Use this page to confirm you wish to delete the following items')

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
                "confirmed": True
            }
        )
        self.assertEqual(num_items - 2, ObjectClass.objects.count())

    def test_delete_by_editor(self):

        self.editor.is_staff = False
        self.editor.save()
        self.editor = self.editor.__class__.objects.get(pk=self.editor.pk)  # decache
        self.assertFalse(self.editor.is_staff)
        self.login_editor()

        num_items = ObjectClass.objects.count()
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
            },
            follow=True
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'bulk_actions_test.actions.StaffDeleteActionForm',
                'safe_to_delete': True,
                'items': [self.item1.id, self.item2.id],
                "confirmed": True
            }
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(num_items, ObjectClass.objects.count())



class BulkDownloadTests(BulkActionsTest, TestCase):
    download_type="txt"

    def setUp(self):
        super().setUp()
        self.celery_result = None
        self.patcher1 = patch('text_download_test.downloader.TestTextDownloader.bulk_download.delay')
        self.patcher2 = patch('aristotle_mdr.views.downloads.async_result')
        self.downloader_download = self.patcher1.start()
        self.async_result = self.patcher2.start()
        self.downloader_download.side_effect = self.txt_bulk_download_cache
        self.async_result.side_effect = self.txt_download_task_retrieve

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()


    def txt_bulk_download_cache(self, properties, iids):
        TestTextDownloader.bulk_download(properties, iids)

        return store_taskresult()


    def txt_download_task_retrieve(self, iid):
        """
        Using taskResult to manage the celery tasks
        :return:
        """
        if not self.celery_result:
            # Creating an instance of fake Celery `AsyncResult` object
            self.celery_result = get_download_result(iid)
        return self.celery_result

    def test_bulk_txt_download_on_permitted_items(self):
        self.login_editor()

        self.assertEqual(self.editor.profile.favourites.count(), 0)
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item2.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_bulk_txt_download_on_forbidden_items(self):
        self.login_editor()

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item4.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            },
            follow=True
        )
        self.assertEqual(len(response.redirect_chain), 2)
        self.assertEqual(response.redirect_chain[0][1], 302)


    def test_bulk_txt_download_on_forbidden_items_by_anonymous_user(self):
        self.logout()

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item4.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            },
            follow=True
        )
        self.assertEqual(len(response.redirect_chain), 2)
        self.assertEqual(response.redirect_chain[0][1], 302)

        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_mdr.forms.bulk_actions.BulkDownloadForm',
                'items': [self.item1.id, self.item4.id],
                "title": "The title",
                "download_type": self.download_type,
                'confirmed': 'confirmed',
            },
        )
        self.assertRedirects(
            response,
            reverse(
                'aristotle:bulk_download',
                kwargs={
                    "download_type": self.download_type,
                }
            )+"?title=The%20title"+"&items=%s&items=%s"%(self.item1.id, self.item4.id)
        , fetch_redirect_response=False)


    def test_content_exists_in_bulk_txt_download_on_permitted_items(self):
        self.login_editor()

        self.item5 = models.DataElementConcept.objects.create(name="DEC1", definition="DEC5 definition", objectClass=self.item2, workgroup=self.wg1)
        self.celery_result = None
        response = self.client.get(
            reverse(
                'aristotle:bulk_download',
                kwargs={
                    "download_type": self.download_type,
                }
            ),
            {
                "items": [self.item1.id, self.item5.id],
                "title": "The title",
            }
        , follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:preparing_download', args=['txt']) +
                         '?items={}&items={}&bulk=True&title=The+title'.format(self.item1.id, self.item5.id))
        self.assertTrue(self.async_result.called)
        self.assertTrue(self.downloader_download.called)
        self.assertEqual(len(self.downloader_download.mock_calls), 1)
        self.assertEqual(len(self.async_result.mock_calls), 1)

        response = self.client.get(reverse('aristotle:start_download', args=['txt']) + '?' + response.request['QUERY_STRING'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.downloader_download.called)
        self.assertEqual(len(self.downloader_download.mock_calls), 1)
        self.assertEqual(len(self.async_result.mock_calls), 2)

        self.assertContains(response, self.item1.name)
        self.assertContains(response, self.item2.name)  # Will be in as its a component of DEC5
        self.assertContains(response, self.item5.name)

        self.assertContains(response, self.item1.definition)
        self.assertContains(response, self.item2.definition)  # Will be in as its a component of DEC5
        self.assertContains(response, self.item5.definition)
