from django.test import TestCase, tag, override_settings, modify_settings
from django.contrib.auth import get_user_model

from aristotle_bg_workers.tasks import download
from aristotle_mdr.models import ObjectClass


class DownloadsTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='fake@example.com',
            password='1234'
        )
        self.item = ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.user
        )

    @override_settings(ARISTOTLE_SETTINGS={'DOWNLOADERS': ['aristotle_pdf.downloader.PDFDownloader']})
    @modify_settings(INSTALLED_APPS={'append': 'aristotle_pdf'})
    def test_download_task(self):
        result = download('pdf', [self.item.id], self.user.id)
        self.assertTrue(result)
