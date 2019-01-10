from django.test import TestCase, tag, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from aristotle_bg_workers.tasks import download
from aristotle_mdr import models
from aristotle_mdr.tests.utils import AristotleTestUtils, AsyncResultMock, FakeDownloader

from unittest.mock import patch, MagicMock


@override_settings(ARISTOTLE_SETTINGS={'DOWNLOADERS': ['aristotle_mdr.tests.utils.FakeDownloader']})
class DownloadsTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.item = models.ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.editor
        )
        self.item2 = models.Property.objects.create(
            name='Defense',
            definition='Defense',
            submitter=self.editor
        )
        self.item3 = models.DataElementConcept.objects.create(
            name='Pokemon - Defense',
            definition='A pokemons defense',
            submitter=self.editor
        )

    def setupFakeTaskCreator(self, mock_task_creator):
        fakeResult = AsyncResultMock(20)
        mock_task_creator.return_value = fakeResult

    def post_dl_options(self, querystring):
        url = reverse('aristotle:download_options', args=['txt']) + querystring
        postdata = {
            'include_supporting': True,
            'email_copy': True
        }

        response = self.client.post(url, postdata)
        return response

    @patch('aristotle_bg_workers.tasks.get_download_class')
    def test_download_task(self, fake_get_dl_class):
        # Setup mocks
        fake_dl_class = MagicMock()
        fake_get_dl_class.return_value = fake_dl_class
        # Call task
        result = download('fake', [self.item.id], self.editor.id)
        # Check mocks
        self.assertIsNotNone(result)
        fake_dl_class.assert_called_once_with([self.item.id], self.editor.id, {})
        fake_dl_class().download.assert_called_once()

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
            {'include_supporting': True, 'email_copy': True}
        )

    @patch('aristotle_mdr.views.downloads.download.delay')
    def test_download_view_starts_task(self, mock_task_creator):
        self.setupFakeTaskCreator(mock_task_creator)
        response = self.reverse_get(
            'aristotle:download',
            reverse_args=['fake', self.item.id],
            status_code=200
        )

        mock_task_creator.assert_called_once_with('fake', [self.item.id], None, {})

    @patch('aristotle_mdr.views.downloads.download.delay')
    def test_bulk_download_view_starts_task(self, mock_task_creator):
        self.setupFakeTaskCreator(mock_task_creator)
        url = reverse('aristotle:bulk_download', args=['fake'])
        url += '?items={}&items={}&items={}'.format(self.item.id, self.item2.id, self.item3.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        id_list = [self.item.id, self.item2.id, self.item3.id]
        mock_task_creator.assert_called_once_with('fake', id_list, None, {})

    def test_download_404_when_invalid_type(self):
        self.reverse_get(
            'aristotle:download',
            reverse_args=['jpg', self.item.id],
            status_code=404
        )

    @patch('aristotle_mdr.views.downloads.download.delay')
    def test_task_started_with_options(self, mock_task_creator):
        self.setupFakeTaskCreator(mock_task_creator)
        options = {
            'include_supporting': True,
            'email_copy': True
        }

        session = self.client.session
        session['download_options'] = options
        session.save()

        response = self.reverse_get(
            'aristotle:download',
            reverse_args=['fake', self.item.id],
            status_code=200
        )

        mock_task_creator.assert_called_once_with('fake', [self.item.id], None, options)


class DownloderTestCase(AristotleTestUtils, TestCase):
    """
    Testing functionality defined in the base downloader
    """

    def setUp(self):
        super().setUp()
        self.item = models.ObjectClass.objects.create(
            name='Pokemon',
            definition='Pocket Monsters',
            submitter=self.editor
        )
        self.item2 = models.Property.objects.create(
            name='Defense',
            definition='Defense',
            submitter=self.editor
        )
        self.item3 = models.DataElementConcept.objects.create(
            name='Pokemon - Defense',
            definition='A pokemons defense',
            submitter=self.editor
        )
        self.item4 = models.Property.objects.create(
            name='Attack',
            definition='Attack',
            submitter=self.viewer
        )

    def test_file_path_auth_user(self):
        downloader = FakeDownloader([self.item.id], self.editor.id, {'include_supporting': True})
        path = downloader.get_filepath()
        self.assertRegex(path, '[0-9]+/[0-9a-f]+/download.fak')

    def test_file_path_anon_user(self):
        # Make public so we dont get a permission denied
        self.make_item_public(self.item, self.ra)
        # Setup downloader get path
        downloader = FakeDownloader([self.item.id], None, {'include_supporting': True})
        path = downloader.get_filepath()
        self.assertRegex(path, 'anon/[0-9a-f]+/download.fak')

    def test_file_not_created_if_can_be_retrieved(self):
        fake_url = 'http://www.example.com/existing/file.fak'
        with patch.object(FakeDownloader, 'retrieve_file', return_value=fake_url):
            downloader = FakeDownloader([self.item.id], self.editor.id, {'include_supporting': True})
            url = downloader.download()
            self.assertEqual(url, fake_url)

    def test_items_restricted_to_visible_only(self):
        downloader = FakeDownloader([self.item.id, self.item4.id], self.viewer.id, {})
        self.assertEqual(downloader.numitems, 1)
        self.assertEqual(downloader.items[0].id, self.item4.id)

    def test_exception_raised_if_no_items_visible(self):
        with self.assertRaises(PermissionDenied):
            downloader = FakeDownloader([self.item.id], self.viewer.id, {})
