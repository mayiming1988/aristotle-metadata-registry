from django.test import TestCase

from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models
from aristotle_mdr.downloader import HTMLDownloader


class TestHTMLDownloader(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.animal = models.ObjectClass.objects.create(
            name='Animal',
            definition='An animal or animal like object',
            submitter=self.editor
        )
        self.speed = models.Property.objects.create(
            name='Speed',
            definition='Quickness',
        )
        self.aspeed = models.DataElementConcept.objects.create(
            name='Animal - Speed',
            definition='An animals speed',
            objectClass=self.animal,
            property=self.speed,
            submitter=self.editor
        )

    def test_generates_html_bytes(self):
        downloader = HTMLDownloader([self.animal.id], self.editor.id, {})
        html = downloader.get_html()
        self.assertEqual(type(html), bytes)

    def test_creates_file(self):
        downloader = HTMLDownloader([self.animal.id], self.editor.id, {})
        fileobj = downloader.create_file()
        self.assertIsNotNone(fileobj)

    def test_content_exists_in_bulk_html_download_on_permitted_items(self):
        downloader = HTMLDownloader([self.animal.id, self.aspeed.id], self.editor.id, {})
        html = downloader.get_html().decode()
        self.assertTrue(self.animal.definition in html)
        self.assertTrue(self.aspeed.definition in html)

    def test_content_not_exists_in_bulk_html_download_on_forbidden_items(self):
        downloader = HTMLDownloader([self.animal.id, self.aspeed.id, self.speed.id], self.editor.id, {})
        html = downloader.get_html().decode()
        self.assertTrue(self.animal.definition in html)
        self.assertTrue(self.aspeed.definition in html)
        self.assertFalse(self.speed.definition in html)


class PDFDownloaderTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.item = models.ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.editor
        )
