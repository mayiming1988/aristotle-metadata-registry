from django.test import TestCase, tag, override_settings, modify_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from aristotle_bg_workers.tasks import download
from aristotle_mdr.models import ObjectClass
from aristotle_mdr.tests.utils import AristotleTestUtils


class DownloadsTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.editor
        )

    def post_dl_options(self, querystring):
        url = reverse('aristotle:download_options', args=['txt']) + querystring
        postdata = {
            'include_supporting': True,
            'email_copy': True
        }

        response = self.client.post(url, postdata)
        return response

    @override_settings(ARISTOTLE_SETTINGS={'DOWNLOADERS': ['aristotle_pdf.downloader.PDFDownloader']})
    @modify_settings(INSTALLED_APPS={'append': 'aristotle_pdf'})
    def test_download_task(self):
        result = download('pdf', [self.item.id], self.editor.id)
        self.assertIsNotNone(result)

    def test_dl_options_get_no_items(self):
        url = reverse('aristotle:download_options', args=['txt'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_dl_options_get_with_items(self):
        url = reverse('aristotle:download_options', args=['txt']) + '?items=9'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_dl_options_redirect(self):
        response = self.post_dl_options('?items=1')
        self.assertEqual(response.status_code, 302)

        expected_url = reverse('aristotle:download', args=['txt', '1'])
        self.assertEqual(response.url, expected_url)

    def test_dl_options_redirect(self):
        response = self.post_dl_options('?items=1&items=2')
        self.assertEqual(response.status_code, 302)

        expected_url = reverse('aristotle:bulk_download', args=['txt']) + '?items=1&items=2'
        self.assertEqual(response.url, expected_url)

    def test_dl_options_stores_options(self):
        response = self.post_dl_options('?items=4')
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.client.session['download_options'],
            {
                'include_supporting': True,
                'email_copy': True
            }
        )
