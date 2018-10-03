from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings
from django.utils import timezone

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
from aristotle_mdr.utils import url_slugify_concept
from aristotle_mdr.forms.creation_wizards import (
    WorkgroupVerificationMixin,
    CheckIfModifiedMixin
)

from aristotle_mdr.utils import setup_aristotle_test_environment
setup_aristotle_test_environment()

from aristotle_mdr.tests import utils
from django.contrib.auth import get_user_model
from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_pdf.downloader import get_download_template_path_for_item, PDFDownloader, render_to_pdf
from aristotle_mdr.utils import downloads as download_utils
from aristotle_mdr.tests.utils import store_taskresult, get_download_result
from django.core.cache import cache
from aristotle_pdf.downloader import PDFDownloader
import datetime

from mock import patch


def setUpModule():
    from django.core.management import call_command
    call_command('load_aristotle_help', verbosity=0, interactive=False)


class LoggedInViewConceptPages(utils.LoggedInViewPages):
    defaults = {}
    def setUp(self):
        super(LoggedInViewConceptPages, self).setUp()
        LoggedInViewConceptPages.result = None
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

    def pdf_download_cache(properties, iid):
        User = get_user_model()
        user = properties['user']
        user = User.objects.get(email=user)

        item = MDR._concept.objects.get_subclass(pk=iid)
        item = get_if_user_can_view(item.__class__, user, iid)
        template = get_download_template_path_for_item(item, PDFDownloader.download_type)

        sub_items = [
            (obj_type, qs.visible(user).order_by('name').distinct())
            for obj_type, qs in item.get_download_items()
        ]

        cache.set(download_utils.get_download_cache_key(iid, user), (render_to_pdf(template, {
            'title': "PDF Download for {obj.name}".format(obj=item),
            'item': item,
            'subitems': sub_items,
            'tableOfContents': len(sub_items) > 0,
            'view': properties['view'].lower(),
            'pagesize': properties['page_size'],
        }), 'application/pdf'))
        tr = store_taskresult('123-456-789-{}'.format(iid), 'Test Task {}'.format(iid), user)
        tr.save()

        return tr

    def pdf_download_task_retrieve(iid):
        if not LoggedInViewConceptPages.result:
            # Creating an instance of fake Celery `AsyncResult` object
            LoggedInViewConceptPages.result = get_download_result(iid)
        return LoggedInViewConceptPages.result

    @patch('aristotle_pdf.downloader.PDFDownloader.download.delay', pdf_download_cache)
    @patch('aristotle_mdr.views.downloads.async_result', pdf_download_task_retrieve)
    def test_su_can_download_pdf(self):
        self.login_superuser()
        LoggedInViewConceptPages.result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:preparing_download', args=[self.item1.id]))

        response = self.client.get(reverse('aristotle:preparing_download', args=[self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:start_download', args=[self.item1.id]))

        LoggedInViewConceptPages.result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item2.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:preparing_download', args=[self.item2.id]))

        response = self.client.get(reverse('aristotle:preparing_download', args=[self.item2.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:start_download', args=[self.item2.id]))

    @patch('aristotle_pdf.downloader.PDFDownloader.download.delay', pdf_download_cache)
    @patch('aristotle_mdr.views.downloads.async_result', pdf_download_task_retrieve)
    def test_editor_can_download_pdf(self):
        self.login_editor()
        LoggedInViewConceptPages.result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:preparing_download', args=[self.item1.id]))

        response = self.client.get(reverse('aristotle:preparing_download', args=[self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:start_download', args=[self.item1.id]))

        LoggedInViewConceptPages.result = None
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item2.id]))
        self.assertEqual(response.status_code,403)

    @patch('aristotle_pdf.downloader.PDFDownloader.download.delay', pdf_download_cache)
    @patch('aristotle_mdr.views.downloads.async_result', pdf_download_task_retrieve)
    def test_viewer_can_download_pdf(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:download',args=['pdf',self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:preparing_download', args=[self.item1.id]))

        response = self.client.get(reverse('aristotle:preparing_download',args=[self.item1.id]), follow=True)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.redirect_chain[0][0], reverse('aristotle:start_download', args=[self.item1.id]))

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
