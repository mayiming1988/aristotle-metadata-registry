from django.test import TestCase, tag

from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models
from aristotle_mdr.contrib.aristotle_pdf.downloader import PDFDownloader


@override_settings(ARISTOTLE_SETTINGS={
    'DOWNLOADERS': ['aristotle_mdr.contrib.aristotle_pdf.downloaders.PDFDownloader']}
)
class PDFDownloaderTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = models.ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.editor
        )

    @tag('pdf')
    def test_pdf_download_generates_file(self):
        downloader = PDFDownloader([self.item.id], self.editor.id, {})
        fileobj = downloader.create_file()
        self.assertTrue(fileobj.size > 0)
