from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.tests.utils as utils
from django.urls import reverse
from django.template.loader import select_template
from django.template import TemplateSyntaxError, Context
from django.core.cache import cache

from aristotle_mdr.utils import setup_aristotle_test_environment, downloads as download_utils, get_download_template_path_for_item
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr import models as MDR
from django.contrib.auth import get_user_model
from aristotle_mdr.tests.utils import AsyncResultMock, store_taskresult, get_download_result

from unittest import skip

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


    def txt_download_cache(props, iid):
        """
        Similar to the get_download_config method.
        :param iid:
        :return:
        """
        # retrieving a viewer user
        User = get_user_model()
        user = User.objects.get(email=props['user'])

        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)

        template = get_download_template_path_for_item(item, TextDownloader.txt_download_type)
        template = select_template([template])
        context = {'item': item}
        txt = template.render(context)

        cache.set(download_utils.get_download_cache_key(iid, user), (txt, 'text/plain'))
        tr = store_taskresult('123-456-789-{}'.format(iid), 'Test Task {}'.format(iid), user)
        tr.save()

        return tr

    def txt_download_task_retrieve(iid):
        """
        Using taskResult to manage the celery tasks
        :return:
        """
        if not TextDownloader.result:
            # Creating an instance of fake Celery `AsyncResult` object
            TextDownloader.result = get_download_result(iid)
        return TextDownloader.result


    @skip('Deprecated Test case')
    def test_logged_in_user_text_downloads(self):
        self.login_editor()
        oc = models.ObjectClass.objects.create(name="OC1", workgroup=self.wg1)
        de = models.DataElement.objects.create(name="DE1", definition="A test data element", workgroup=self.wg1)
        dec = models.DataElementConcept.objects.create(name="DEC", workgroup=self.wg1)
        de2 = models.DataElement.objects.create(name="DE2", workgroup=self.wg2)

        response = self.client.get(reverse('aristotle:download', args=['txt', oc.id]))
        # This template does not exist on purpose and will throw an error
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('aristotle:download', args=['txt', de.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, de.name)
        self.assertContains(response, de.definition)

        response = self.client.get(reverse('aristotle:download', args=['txt', de2.id]))
        # This item is not visible to the logged in user and will throw an error
        self.assertEqual(response.status_code, 403)

        with self.assertRaises(TemplateSyntaxError):
            # This template is broken on purpose and will throw an error
            response = self.client.get(reverse('aristotle:download', args=['txt', dec.id]))


    @patch('text_download_test.downloader.TestTextDownloader.download.delay', txt_download_cache)
    @patch('aristotle_mdr.views.downloads.async_result', txt_download_task_retrieve)
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

        # This template does not exist on purpose and will throw an error
        self.assertEqual(response.status_code, 404)

        # Initiating 2nd download
        TextDownloader.result = None
        response = self.client.get(reverse('aristotle:download', args=['txt', self.de.id]))
        self.assertRedirects(response, reverse('aristotle:preparing_download', args=[self.de.id]))

        self.assertEqual(response.status_code, 302)


        # calling the preparing download page to see if the download is available complete
        response = self.client.get(reverse('aristotle:preparing_download', args=[self.de.id]))

        # TODO: Test if the functions are called.
        self.assertRedirects(response, reverse('aristotle:start_download', args=[self.de.id]), fetch_redirect_response=False)
        response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.de.definition)

        # Initiating 3rd download
        TextDownloader.result = None
        response = self.client.get(reverse('aristotle:download', args=['txt', self.de2.id]), follow=True)
        self.assertEqual(response.status_code, 403)

        with self.assertRaises(TemplateSyntaxError):
            # This template is broken on purpose and will throw an error
            response = self.client.get(reverse('aristotle:download', args=['txt', self.dec.id]), follow=True)
