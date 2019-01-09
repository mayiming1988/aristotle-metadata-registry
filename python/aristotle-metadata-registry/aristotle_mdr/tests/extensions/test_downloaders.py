from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.tests.utils as utils
from django.urls import reverse
from django.template import TemplateSyntaxError

from aristotle_mdr.utils import setup_aristotle_test_environment
from aristotle_mdr.tests.utils import store_taskresult, get_download_result
from aristotle_mdr.tests.apps.text_download_test.downloader import TestTextDownloader

from mock import patch

setup_aristotle_test_environment()


class TextDownloader(utils.LoggedInViewPages, TestCase):
    """
    Test the text downloader feature
    """

    def setUp(self):
        super(TextDownloader, self).setUp()
        TextDownloader.txt_download_type = "txt"
        TextDownloader.result = None
        self.patcher1 = patch('text_download_test.downloader.TestTextDownloader.download.delay')
        self.patcher2 = patch('aristotle_mdr.views.downloads.async_result')
        self.downloader_download = self.patcher1.start()
        self.async_result = self.patcher2.start()
        self.downloader_download.side_effect = self.txt_download_cache
        self.async_result.side_effect = self.txt_download_task_retrieve

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def txt_download_cache(self, props, iid):
        """
        Similar to the Text download method.
        :param iid:
        :return:
        """
        TestTextDownloader.download(props, iid)
        return store_taskresult()

    def txt_download_task_retrieve(self, iid):
        """
        Using taskResult to manage the celery tasks
        :return:
        """
        if not TextDownloader.result:
            # Creating an instance of fake Celery `AsyncResult` object
            TextDownloader.result = get_download_result(iid)
        return TextDownloader.result

    def test_logged_in_user_text_download_initiates(self):
        """
        Tests the failing txt download
        Tests the passing txt download celery worker initiated
        Tests the passing txt download redirect to preparing download page.
        :return:
        """
        self.login_editor()
        self.oc = models.ObjectClass.objects.create(name="OC1", workgroup=self.wg1)
        self.de = models.DataElement.objects.create(name="DE1", definition="A test data element", workgroup=self.wg1)
        self.dec = models.DataElementConcept.objects.create(name="DEC", workgroup=self.wg1)
        self.de2 = models.DataElement.objects.create(name="DE2", workgroup=self.wg2)

        TextDownloader.result = None
        response = self.client.get(reverse('aristotle:download', args=['txt', self.oc.id]))
        self.assertEqual(len(self.downloader_download.mock_calls), 1)
        self.assertTrue(self.downloader_download.called)

        # This template does not exist on purpose and will throw an error
        self.assertEqual(response.status_code, 404)

        # Initiating 2nd download
        TextDownloader.result = None
        response = self.client.get(reverse('aristotle:download', args=['txt', self.de.id]))
        self.assertEqual(len(self.downloader_download.mock_calls), 2)
        self.assertRedirects(response, reverse('aristotle:preparing_download', args=['txt']) +
                             '?items={}&title=Auto-Generated+Document'.format(self.de.id))
        self.assertTrue(self.async_result.called)
        self.assertEqual(len(self.downloader_download.mock_calls), 2)
        self.assertEqual(len(self.async_result.mock_calls), 1)
        self.assertEqual(response.status_code, 302)

        # calling the preparing download page to see if the download is available complete
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.async_result.called)
        self.assertEqual(len(self.async_result.mock_calls), 2)


        response = self.client.get(reverse('aristotle:start_download', args=['txt']) + '?items={}&title=Auto-Generated+Document'.format(self.de.id))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.async_result.called)
        self.assertEqual(len(self.async_result.mock_calls), 3)

        self.assertContains(response, self.de.definition)

        # Initiating 3rd download
        TextDownloader.result = None
        response = self.client.get(reverse('aristotle:download', args=['txt', self.de2.id]), follow=True)
        self.assertEqual(response.status_code, 403)

        with self.assertRaises(TemplateSyntaxError):
            # This template is broken on purpose and will throw an error
            response = self.client.get(reverse('aristotle:download', args=['txt', self.dec.id]), follow=True)
