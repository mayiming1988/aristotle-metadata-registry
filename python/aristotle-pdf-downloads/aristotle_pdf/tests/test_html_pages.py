from django.core.urlresolvers import reverse
from django.test import TestCase

import aristotle_mdr.models as models
from aristotle_mdr.forms.creation_wizards import (
    WorkgroupVerificationMixin,
    CheckIfModifiedMixin
)

from aristotle_mdr.utils import setup_aristotle_test_environment
setup_aristotle_test_environment()

from aristotle_mdr.tests import utils
from aristotle_pdf.downloader import  PDFDownloader
from aristotle_mdr.tests.utils import store_taskresult, get_download_result

from mock import patch


def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0, interactive=False)


class LoggedInViewConceptPages(utils.LoggedInViewPages):
    defaults = {}
    # This result represents the result from the download view

    def setUp(self):
        super(LoggedInViewConceptPages, self).setUp()
        self.celery_result = None
        self.item1 = self.itemType.objects.create(
            name="Test Item 1 (visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg1,
            **self.defaults
        )
        self.item2 = self.itemType.objects.create(
            name="Test Item 2 (NOT visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg2,
            **self.defaults
        )
        self.item3 = self.itemType.objects.create(
            name="Test Item 3 (visible to tested viewers)",
            definition="my definition",
            workgroup=self.wg1,
            **self.defaults
        )

        # Setting up patches
        self.patcher1 = patch('aristotle_pdf.downloader.PDFDownloader.download.delay')
        self.patcher2 = patch('aristotle_mdr.views.downloads.async_result')
        self.downloader_download = self.patcher1.start()
        self.async_result = self.patcher2.start()
        self.downloader_download.side_effect = self.pdf_download_cache
        self.async_result.side_effect = self.pdf_download_task_retrieve

    def tearDown(self):
        # Tearing down patches
        self.patcher1.stop()
        self.patcher2.stop()

    def pdf_download_cache(self, properties, iid):
        PDFDownloader.download(properties, iid)
        return store_taskresult()

    def pdf_download_task_retrieve(self, iid):
        if not self.celery_result:
            # Creating an instance of fake Celery `AsyncResult` object
            self.celery_result = get_download_result(iid)
        return self.celery_result

    def test_su_can_download_pdf(self):
        self.login_superuser()
        self.celery_result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf', self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('aristotle:preparing_download', args=['pdf']) in response.redirect_chain[0][0])
        self.assertTrue(self.downloader_download.called)
        self.assertTrue(self.async_result.called)

        response = self.client.get('{}?{}'.format(
            reverse('aristotle:start_download', args=['pdf']),
            response.request['QUERY_STRING']),
        )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.async_result.called)

        self.celery_result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf', self.item2.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('aristotle:preparing_download', args=['pdf']) in response.redirect_chain[0][0])
        self.assertTrue(self.downloader_download.called)
        self.assertTrue(self.async_result.called)

        response = self.client.get('{}?{}'.format(
            reverse('aristotle:start_download', args=['pdf']),
            response.request['QUERY_STRING']),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.async_result.called)

    def test_editor_can_download_pdf(self):
        self.login_editor()
        self.celery_result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf', self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('aristotle:preparing_download', args=['pdf']) in response.redirect_chain[0][0])
        self.assertTrue(self.downloader_download.called)
        self.assertTrue(self.async_result.called)

        response = self.client.get('{}?{}'.format(
            reverse('aristotle:start_download', args=['pdf']),
            response.request['QUERY_STRING']),
        )
        self.assertEqual(response.status_code,200)
        self.assertTrue(self.async_result.called)

        self.celery_result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf', self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_viewer_can_download_pdf(self):
        self.login_viewer()
        self.celery_result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf', self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.redirect_chain), 1)
        self.assertTrue(reverse('aristotle:preparing_download', args=['pdf']) in response.redirect_chain[0][0])
        self.assertTrue(self.downloader_download.called)
        self.assertTrue(self.async_result.called)
        self.assertEqual(len(self.downloader_download.mock_calls), 1)
        self.assertEqual(len(self.async_result.mock_calls), 1)

        response = self.client.get('{}?{}'.format(
            reverse('aristotle:start_download', args=['pdf']),
            response.request['QUERY_STRING']),
        )

        self.assertEqual(response.status_code,200)
        self.assertTrue(self.async_result.called)
        self.assertEqual(len(self.async_result.mock_calls), 2)

        self.celery_result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item2.id]))
        self.assertEqual(response.status_code,403)


class ObjectClassViewPage(LoggedInViewConceptPages, TestCase):
    url_name='objectClass'
    itemType=models.ObjectClass
class PropertyViewPage(LoggedInViewConceptPages, TestCase):
    url_name='property'
    itemType=models.Property
class UnitOfMeasureViewPage(LoggedInViewConceptPages, TestCase):
    url_name='unitOfMeasure'
    itemType=models.UnitOfMeasure
class ValueDomainViewPage(LoggedInViewConceptPages, TestCase):
    url_name='valueDomain'
    itemType=models.ValueDomain
    def setUp(self):
        super(ValueDomainViewPage, self).setUp()

        for i in range(4):
            models.PermissibleValue.objects.create(
                value=i,meaning="test permissible meaning %d"%i,order=i,valueDomain=self.item1
                )
        for i in range(4):
            models.SupplementaryValue.objects.create(
                value=i,meaning="test supplementary meaning %d"%i,order=i,valueDomain=self.item1
                )

class ConceptualDomainViewPage(LoggedInViewConceptPages, TestCase):
    url_name='conceptualDomain'
    itemType=models.ConceptualDomain
class DataElementConceptViewPage(LoggedInViewConceptPages, TestCase):
    url_name='dataElementConcept'
    itemType=models.DataElementConcept
    run_cascade_tests = True

    def setUp(self, *args, **kwargs):
        super(DataElementConceptViewPage, self).setUp(*args, **kwargs)
        self.oc = models.ObjectClass.objects.create(
            name="sub item OC",
            workgroup=self.item1.workgroup,
        )
        self.prop = models.Property.objects.create(
            name="sub item prop",
            workgroup=self.item1.workgroup
        )
        self.item1.objectClass = self.oc
        self.item1.property = self.prop
        self.item1.save()
        self.assertTrue(self.oc.can_view(self.editor))
        self.assertTrue(self.prop.can_view(self.editor))


class DataElementViewPage(LoggedInViewConceptPages, TestCase):
    url_name='dataElement'
    itemType=models.DataElement


class DataElementDerivationViewPage(LoggedInViewConceptPages, TestCase):
    url_name='dataelementderivation'
    itemType=models.DataElementDerivation
