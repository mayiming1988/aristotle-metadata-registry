# coding: utf8
from django.core.urlresolvers import reverse
from django.test import TestCase
import aristotle_mdr.models as models


from aristotle_mdr.utils import setup_aristotle_test_environment

from mock import patch
from aristotle_mdr.tests.utils import store_taskresult, get_download_result
from aristotle_pdf.downloader import PDFDownloader

setup_aristotle_test_environment()

from aristotle_mdr.tests.main.test_bulk_actions import BulkActionsTest

class QuickPDFDownloadTests(BulkActionsTest, TestCase):

    def setUp(self):
        super().setUp()
        self.celery_result = None
        self.patcher1 = patch('aristotle_pdf.downloader.PDFDownloader.bulk_download.delay')
        self.patcher2 = patch('aristotle_mdr.views.downloads.async_result')
        self.downloader_download = self.patcher1.start()
        self.async_result = self.patcher2.start()
        self.downloader_download.side_effect = self.pdf_bulk_download_cache
        self.async_result.side_effect = self.pdf_download_task_retrieve

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def pdf_bulk_download_cache(self, properties, iids):
        PDFDownloader.bulk_download(properties, iids)

        return store_taskresult()

    def pdf_download_task_retrieve(self, iid):
        """
        Using taskResult to manage the celery tasks
        :return:
        """
        if not self.celery_result:
            # Creating an instance of fake Celery `AsyncResult` object
            self.celery_result = get_download_result(iid)
        return self.celery_result

    def test_bulk_quick_pdf_download_on_permitted_items(self):
        self.login_editor()

        self.assertEqual(self.editor.profile.favourites.count(), 0)
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_pdf.bulk_actions.QuickPDFDownloadForm',
                'items': [self.item1.id, self.item2.id],
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_bulk_quick_pdf_download_on_forbidden_items(self):
        self.login_editor()

        self.assertEqual(self.editor.profile.favourites.count(), 0)
        response = self.client.post(
            reverse('aristotle:bulk_action'),
            {
                'bulkaction': 'aristotle_pdf.bulk_actions.QuickPDFDownloadForm',
                'items': [self.item1.id, self.item4.id],
            },
            follow=True
        )
        self.assertEqual(len(response.redirect_chain), 2)
        self.assertEqual(response.redirect_chain[0][1], 302)


class BulkDownloadTests(BulkActionsTest, TestCase):
    download_type="pdf"

    def setUp(self):
        super().setUp()
        self.celery_result = None
        self.patcher1 = patch('aristotle_pdf.downloader.PDFDownloader.bulk_download.delay')
        self.patcher2 = patch('aristotle_mdr.views.downloads.async_result')
        self.downloader_download = self.patcher1.start()
        self.async_result = self.patcher2.start()
        self.downloader_download.side_effect = self.pdf_bulk_download_cache
        self.async_result.side_effect = self.pdf_download_task_retrieve

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def pdf_bulk_download_cache(self, properties, iids):
        PDFDownloader.bulk_download(properties, iids)

        return store_taskresult()

    def pdf_download_task_retrieve(self, iid):
        """
        Using taskResult to manage the celery tasks
        :return:
        """
        if not self.celery_result:
            # Creating an instance of fake Celery `AsyncResult` object
            self.celery_result = get_download_result(iid)
        return self.celery_result


    def test_bulk_pdf_download_on_permitted_items(self):
        self.login_editor()
        self.celery_result = None
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

    def test_bulk_pdf_download_on_forbidden_items(self):
        self.login_editor()
        self.celery_result = None
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


    def test_bulk_pdf_download_on_forbidden_items_by_anonymous_user(self):
        self.logout()
        self.celery_result = None
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

    def test_content_exists_in_bulk_pdf_download_on_permitted_items(self):
        self.login_editor()
        self.celery_result = None

        self.item5 = models.DataElementConcept.objects.create(name="DEC1", definition="DEC5 definition", objectClass=self.item2, workgroup=self.wg1)

        response = self.client.get(
            reverse(
                'aristotle:bulk_download',
                kwargs={
                    "download_type": self.download_type,
                }
            ),
            {
                "items": [self.item1.id, self.item5.id],
                "title": "The title".encode('utf-8'),
                "html": True  # Force HTML to debug content
            }
        ,follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0],
                         reverse('aristotle:preparing_download', args=['pdf']) +
                         "?items=%s&items=%s" % (self.item1.id, self.item5.id) + '&html=True&bulk=True&title=The+title'
                         )
        self.assertTrue(self.async_result.called)
        self.assertTrue(self.downloader_download.called)
        self.assertEqual(len(self.downloader_download.mock_calls), 1)
        self.assertEqual(len(self.async_result.mock_calls), 1)

        response = self.client.get(reverse('aristotle:start_download', args=['pdf']) + '?' +response.request['QUERY_STRING'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.downloader_download.called)
        self.assertEqual(len(self.downloader_download.mock_calls), 1)
        self.assertEqual(len(self.async_result.mock_calls), 2)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item1.name)
        self.assertContains(response, self.item2.name)  # Will be in as its a component of DEC5
        self.assertContains(response, self.item5.name)

        self.assertContains(response, self.item1.definition)
        self.assertContains(response, self.item2.definition)  # Will be in as its a component of DEC5
        self.assertContains(response, self.item5.definition)


    def test_content_not_exists_in_bulk_pdf_download_on_forbidden_items(self):
        self.logout()
        self.celery_result = None

        self.item5 = models.DataElementConcept.objects.create(name="DEC1", definition="DEC5 definition", objectClass=self.item2, workgroup=self.wg1)

        response = self.client.get(
            reverse(
                'aristotle:bulk_download',
                kwargs={
                    "download_type": self.download_type,
                }
            ),
            {
                "items": [self.item1.id, self.item4.id],
                "title": "The title",
                "html": True  # Force HTML to debug content
            }
            , follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertEqual(response.redirect_chain[0][0],
                         reverse('aristotle:preparing_download', args=["pdf"]) +
                         "?items=%s&items=%s" % (self.item1.id, self.item4.id) + '&html=True&bulk=True&title=The+title')
        self.assertTrue(self.async_result.called)
        self.assertTrue(self.downloader_download.called)
        self.assertEqual(len(self.downloader_download.mock_calls), 1)
        self.assertEqual(len(self.async_result.mock_calls), 1)

        response = self.client.get(reverse('aristotle:start_download', args=['pdf']) + '?' +response.request['QUERY_STRING'])
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.item1.name)
        self.assertNotContains(response, self.item2.name)  # Will be in as its a component of DEC5
        self.assertNotContains(response, self.item5.name)

        self.assertNotContains(response, self.item1.definition)
        self.assertNotContains(response, self.item2.definition)  # Will be in as its a component of DEC5
        self.assertNotContains(response, self.item5.definition)

