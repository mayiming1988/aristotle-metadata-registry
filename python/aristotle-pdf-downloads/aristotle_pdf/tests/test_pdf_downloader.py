from django.test import TestCase

from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models
from aristotle_mdr.downloader import HTMLDownloader


class TestHTMLDownloader(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = models.ObjectClass.objects.create(
            name='My Objects',
            definition='mine',
            submitter=self.editor
        )

    def test_generates_html_string(self):
        downloader = HTMLDownloader([self.item.id], self.editor.id, {})
        html = downloader.get_html()
        self.assertEqual(type(html), bytes)

    def test_creates_file(self):
        downloader = HTMLDownloader([self.item.id], self.editor.id, {})
        fileobj = downloader.create_file()
        self.assertIsNotNone(fileobj)


class PDFDownloaderTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.item = models.ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.editor
        )
