from django.test import TestCase, tag, override_settings
from unittest import skip

from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models
from aristotle_mdr.contrib.aristotle_pdf.downloader import PDFDownloader

import os
import PyPDF2


@override_settings(ARISTOTLE_SETTINGS={
    'DOWNLOAD_OPTIONS': {'DOWNLOADERS': ['aristotle_mdr.contrib.aristotle_pdf.downloaders.PDFDownloader']}
})
class PDFDownloaderTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = models.ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.editor
        )
        self.basedir = os.path.dirname(__file__)

    @tag('pdf')
    @override_settings(MEDIA_ROOT=os.path.join(os.path.dirname(__file__), 'fixtures'))
    def test_upload_of_cover_page_to_download(self):
        """Test that a cover page can be included in the download"""

        # Submit the cover page
        downloader = PDFDownloader([self.item.id],
                                   self.editor.id,
                                   {'front_page': os.path.join(self.basedir, 'fixtures/cover_page.pdf')})
        pdf_file = downloader.create_file()

        # pdf = PyPDF2.PdfFileReader(pdf_file)
        # first_page = pdf.getPage(0)
        # page_content = first_page.extractText()
        #
        # raise ValueError(page_content.encode('utf-8'))

    @tag('pdf')
    @skip('wkhtmltopdf not installed on travis')
    def test_pdf_download_generates_file(self):
        downloader = PDFDownloader([self.item.id], self.editor.id, {})
        fileobj = downloader.create_file()
        self.assertTrue(fileobj.size > 0)

    @tag('pdf_su')
    @skip('wkhtmltopdf not installed on travis')
    def test_pdf_download_generates_file_superuser(self):
        downloader = PDFDownloader([self.item.id], self.su.id, {})
        fileobj = downloader.create_file()
        self.assertTrue(fileobj.size > 0)
