from django.test import TestCase

import aristotle_mdr.models as models
import aristotle_mdr.tests.utils as utils
from django.urls import reverse
from django.template.loader import select_template
from django.template import TemplateSyntaxError, Context
from django.core.cache import cache

from aristotle_mdr.utils import setup_aristotle_test_environment, downloads as download_utils, get_download_template_path_for_item
from aristotle_bg_workers.helpers import store_task
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr import models as MDR
from django_celery_results.models import TaskResult
from django.contrib.auth import get_user_model

from unittest import skip

from celery import current_app, states

from mock import patch, MagicMock

setup_aristotle_test_environment()


class AsyncResultMock:
    """
    This mock AsyncResult class will replace celery's AsyncResult class to facilitate ready and status features
    First attempt to ready() will send a Pending state and the second attempt will make sure it is a success
    """

    def __init__(self, task_id):
        """
        initialize the mock async result
        :param task_id: task_id for mock task
        """
        self.status = states.PENDING
        self.id = task_id
        self.result = ''

    def ready(self):
        """
        not ready in the first try and ready in the next
        returns true once the worker finishes it's task
        :return: bool
        """
        is_ready = self.status == states.SUCCESS

        self.status = states.SUCCESS
        return is_ready

    def successful(self):
        """
        Returns true once the worker finishes it's task successfully
        :return: bool
        """
        return self.status == states.SUCCESS

    def forget(self):
        """
        deletes itself
        :return:
        """
        del self

    def get(self):
        result = self.result
        self.forget()
        return result


class TextDownloader(utils.LoggedInViewPages, TestCase):
    """
    Test the text downloader feature
    """

    def setUp(self):
        super(TextDownloader, self).setUp()
        TextDownloader.txt_download_type = "txt"
        TextDownloader.result = None


    @staticmethod
    def store_taskresult(id, name, user, status='SUCCESS'):
        store_task(id, name, user)

        tr = TaskResult.objects.create(
            task_id=id,
            status=status
        )

        return tr

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
        # Setting the user text
        print('-------------text------------')
        print(txt)

        cache.set(download_utils.get_download_cache_key(iid, user), (txt, 'text/plain'))
        tr = TextDownloader.store_taskresult('123-456-789-{}'.format(iid), 'Test Task {}'.format(iid), user)
        tr.save()

        return tr


    def txt_download_task_retrieve(iid):
        """
        Using taskResult to manage the celery tasks
        :return:
        """
        tr = TaskResult.objects.get(id=iid)
        if not TextDownloader.result:
            TextDownloader.result = AsyncResultMock(tr.task_id)
        return TextDownloader.result

    @skip('Deprecated Test case')
    @patch('text_download_test.downloader.TestTextDownloader.download.delay', txt_download_cache)
    @patch('aristotle_mdr.views.downloads.async_result', txt_download_task_retrieve)
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
        # downloader.return_value = MagicMock()
        response = self.client.get(reverse('aristotle:download', args=['txt', self.oc.id]))

        # This template does not exist on purpose and will throw an error
        self.assertEqual(response.status_code, 404)

        # calling downloading page
        response = self.client.get(reverse('aristotle:download', args=['txt', self.de.id]))
        self.assertRedirects(response, reverse('aristotle:preparing_download', args=[self.de.id]))

        self.assertEqual(response.status_code, 302)

        # calling the preparing download page to see if the download is available complete
        response = self.client.get(reverse('aristotle:preparing_download', args=[self.de.id]))

        # TODO: Test if the functions are called.
        self.assertRedirects(response, reverse('aristotle:start_download', args=[self.de.id]), fetch_redirect_response=False)
        response = self.client.get(response.url)
        import pdb
        pdb.set_trace()
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.de.definition)

        response = self.client.get(reverse('aristotle:download', args=['txt', self.de2.id]), follow=True)
        self.assertEqual(response.status_code, 403)

        with self.assertRaises(TemplateSyntaxError):
            # This template is broken on purpose and will throw an error
            response = self.client.get(reverse('aristotle:download', args=['txt', self.dec.id]), follow=True)
