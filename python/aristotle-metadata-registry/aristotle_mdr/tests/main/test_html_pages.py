from django.conf import settings
from django.core.cache import cache
from django.db.models.fields import CharField, TextField
from django.http import HttpResponse
from django.http import QueryDict
from django.test import TestCase, override_settings, tag, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

import aristotle_mdr.models as models
import aristotle_mdr.perms as perms
import aristotle_mdr.contrib.identifiers.models as ident_models
from aristotle_mdr.contrib.slots.choices import permission_choices
from aristotle_mdr.contrib.custom_fields.models import CustomField, CustomValue
from aristotle_mdr.utils import url_slugify_concept
from aristotle_mdr.forms.creation_wizards import (
    WorkgroupVerificationMixin,
    CheckIfModifiedMixin
)
from aristotle_mdr.tests import utils
from aristotle_mdr.views import ConceptRenderView
from aristotle_mdr.downloader import HTMLDownloader
import datetime
from unittest import mock, skip
import reversion
import json

from aristotle_mdr.tests.utils import store_taskresult, get_download_result

from mock import patch

from aristotle_mdr.templatetags.aristotle_tags import get_dataelements_from_m2m


class AnonymousUserViewingThePages(TestCase):
    def test_homepage(self):
        response = self.client.get(reverse('aristotle:smart_root'))
        self.assertRedirects(response, reverse('aristotle:home'))

    def test_notifications_for_anon_users(self):
        response = self.client.get(reverse('aristotle:home'))
        self.assertEqual(response.status_code,200)
        # Make sure notifications library isn't loaded for anon users as they'll never have notifications.
        self.assertNotContains(response, "notifications/notify.js")
        # At some stage this might need a better test to check the 500 page doesn't show... after notifications is fixed.

    def test_sitemaps(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code,200)
        response = self.client.get("/sitemaps/sitemap_0.xml")
        self.assertEqual(response.status_code,200)

    def test_visible_item(self):
        wg = models.Workgroup.objects.create(name="Setup WG")
        ra = models.RegistrationAuthority.objects.create(name="Test RA")
        item = models.ObjectClass.objects.create(name="Test OC",workgroup=wg)
        s = models.Status.objects.create(
                concept=item,
                registrationAuthority=ra,
                registrationDate=timezone.now(),
                state=ra.locked_state
                )
        response = self.client.get(url_slugify_concept(item))
        # Anonymous users requesting a hidden page will be redirected to login
        self.assertEqual(response.status_code,302)
        s.state = ra.public_state
        s.save()
        response = self.client.get(url_slugify_concept(item))
        self.assertEqual(response.status_code,200)


class LoggedInViewHTMLPages(utils.LoggedInViewPages, TestCase):
    def test_homepage(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:smart_root'))
        self.assertRedirects(response, reverse('aristotle:userHome'))


# Tests that dont require running on all item types
@tag('itempage_general')
class GeneralItemPageTestCase(utils.AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()

        self.item = models.ObjectClass.objects.create(
            name='Test Item',
            definition='Test Item Description',
            submitter=self.editor,
            workgroup=self.wg1
        )
        self.itemid = self.item.id

        self.future_time = timezone.now() + datetime.timedelta(days=30)

        self.cache_key = 'view_cache_ConceptView_{}_{}'.format(
            self.editor.id,
            self.itemid
        )

        self.factory = RequestFactory()

        cache.clear()

    def setup_custom_values(self):
        allfield = CustomField.objects.create(
            order=0,
            name='AllField',
            type='String',
            visibility=permission_choices.public
        )
        authfield = CustomField.objects.create(
            order=1,
            name='AuthField',
            type='String',
            visibility=permission_choices.auth
        )
        wgfield = CustomField.objects.create(
            order=2,
            name='WgField',
            type='String',
            visibility=permission_choices.workgroup
        )
        self.allval = CustomValue.objects.create(
            field=allfield,
            content='All Value',
            concept=self.item
        )
        self.authval = CustomValue.objects.create(
            field=authfield,
            content='Auth Value',
            concept=self.item
        )
        self.wgval = CustomValue.objects.create(
            field=wgfield,
            content='Workgroup Value',
            concept=self.item
        )

    def test_itempage_full_url(self):
        self.login_editor()
        full_url = url_slugify_concept(self.item)
        response = self.client.get(full_url)
        self.assertEqual(response.status_code, 200)

    def test_itempage_redirect_id_only(self):
        self.login_editor()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.itemid],
            status_code=302
        )

        self.assertEqual(response.url, url_slugify_concept(self.item))

    def test_itempage_redirect_wrong_modelslug(self):
        self.login_editor()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.itemid, 'definition', 'wow'],
            status_code=302
        )

        self.assertEqual(response.url, url_slugify_concept(self.item))

    def test_itempage_wrong_model_modelslug(self):
        self.login_editor()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.itemid, 'property', 'wow'],
            status_code=404
        )

    def test_itempage_wrong_name(self):
        self.login_editor()

        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.itemid, 'objectclass', 'wow'],
            status_code=200
        )

    @tag('cache')
    @override_settings(CACHE_ITEM_PAGE=True)
    @skip('Cache mixin not currently used')
    def test_itempage_caches(self):

        # View in the future to avoid modified recently check
        # No flux capacitors required
        with mock.patch('aristotle_mdr.utils.utils.timezone.now') as mock_now:
            mock_now.return_value = self.future_time

            self.login_editor()
            response = self.reverse_get(
                'aristotle:item',
                reverse_args=[self.itemid, 'objectclass', 'test-item'],
                status_code=200
            )

        cached_itempage = cache.get(self.cache_key, None)
        self.assertIsNotNone(cached_itempage)

    @tag('cache')
    @override_settings(CACHE_ITEM_PAGE=True)
    @skip('Cache mixin not currently used')
    def test_itempage_loaded_from_cache(self):

        # Load response into cache
        cache.set(self.cache_key, HttpResponse('wow'))

        # View item page in future
        with mock.patch('aristotle_mdr.utils.utils.timezone.now') as mock_now:
            mock_now.return_value = self.future_time

            self.login_editor()
            response = self.reverse_get(
                'aristotle:item',
                reverse_args=[self.itemid, 'objectclass', 'test-item'],
                status_code=200
            )

            self.assertEqual(response.content, b'wow')

    @tag('cache')
    @override_settings(CACHE_ITEM_PAGE=True)
    @skip('Cache mixin not currently used')
    def test_itempage_not_loaded_from_cache_if_modified(self):

        # Load response into cache
        cache.set(self.cache_key, HttpResponse('wow'))

        # View page now (assumes this test wont take 300 seconds)
        self.login_editor()
        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.itemid, 'objectclass', 'test-item'],
            status_code=200
        )

        self.assertNotEqual(response.content, b'wow')

    @tag('cache')
    @override_settings(CACHE_ITEM_PAGE=True)
    @skip('Cache mixin not currently used')
    def test_itempage_not_loaded_from_cache_if_nocache_set(self):
        cache.set(self.cache_key, HttpResponse('wow'))

        url = reverse('aristotle:item', args=[self.itemid, 'objectclass', 'test-item'])
        url += '?nocache=true'

        # View item page in future
        with mock.patch('aristotle_mdr.utils.utils.timezone.now') as mock_now:
            mock_now.return_value = self.future_time

            self.login_editor()

            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(response.content, b'wow')

    @tag('cache')
    @override_settings(CACHE_ITEM_PAGE=True)
    @skip('Cache mixin not currently used')
    def test_itempage_cached_per_user(self):
        # Load response into cache
        cache.set(self.cache_key, HttpResponse('wow'))

        # View item page in future
        with mock.patch('aristotle_mdr.utils.utils.timezone.now') as mock_now:
            mock_now.return_value = self.future_time

            # Login as different user
            self.login_viewer()
            response = self.reverse_get(
                'aristotle:item',
                reverse_args=[self.itemid, 'objectclass', 'test-item'],
                status_code=200
            )

            self.assertNotEqual(response.content, b'wow')

    @tag('cache')
    @override_settings(CACHE_ITEM_PAGE=False)
    @skip('Cache mixin not currently used')
    def test_itempage_not_loaded_from_cache_if_setting_false(self):
        # Load response into cache
        cache.set(self.cache_key, HttpResponse('wow'))

        # View item page in future
        with mock.patch('aristotle_mdr.utils.utils.timezone.now') as mock_now:
            mock_now.return_value = self.future_time

            # Login as different user
            self.login_editor()
            response = self.reverse_get(
                'aristotle:item',
                reverse_args=[self.itemid, 'objectclass', 'test-item'],
                status_code=200
            )

            self.assertNotEqual(response.content, b'wow')

    @tag('cache')
    @override_settings(CACHE_ITEM_PAGE=False)
    @skip('Cache mixin not currently used')
    def test_response_not_put_into_cache_if_setting_false(self):
        # View in the future to avoid modified recently check
        with mock.patch('aristotle_mdr.utils.utils.timezone.now') as mock_now:
            mock_now.return_value = self.future_time

            self.login_editor()
            response = self.reverse_get(
                'aristotle:item',
                reverse_args=[self.itemid, 'objectclass', 'test-item'],
                status_code=200
            )

        cached_itempage = cache.get(self.cache_key, None)
        self.assertIsNone(cached_itempage)

    @tag('extrav')
    def test_no_extra_versions_created_adv_editor(self):

        oc = models.ObjectClass.objects.create(
            name='Test OC',
            definition='Just a test',
            submitter=self.editor
        )

        prop = models.Property.objects.create(
            name='Test Prop',
            definition='Just a test',
            submitter=self.editor
        )

        dec = models.DataElementConcept.objects.create(
            name='Test DEC',
            definition='Just a test',
            objectClass=oc,
            property=prop,
            submitter=self.editor
        )

        data = utils.model_to_dict_with_change_time(dec)
        data.update({
            'definition': 'More than a test',
            'change_comments': 'A change was made'
        })

        from reversion import models as revmodels
        self.assertEqual(revmodels.Version.objects.count(), 0)

        self.login_editor()
        response = self.reverse_post(
            'aristotle:edit_item',
            data=data,
            status_code=302,
            reverse_args=[dec.id]
        )

        dec = models.DataElementConcept.objects.get(pk=dec.pk)
        self.assertEqual(dec.definition, 'More than a test')

        # Should be 2 version, one for the _concept,
        # one for the data element concept
        self.assertEqual(revmodels.Version.objects.count(), 2)

        from django.contrib.contenttypes.models import ContentType
        concept_ct = ContentType.objects.get_for_model(models._concept)
        dec_ct = ContentType.objects.get_for_model(models.DataElementConcept)

        concept_version = revmodels.Version.objects.get(content_type=concept_ct)
        dec_version = revmodels.Version.objects.get(content_type=dec_ct)

        # check concept version
        self.assertEqual(int(concept_version.object_id), dec._concept_ptr.id)

        # check dec version
        self.assertEqual(int(dec_version.object_id), dec.id)

    @tag('version')
    def test_display_version_concept_info(self):

        self.item.references = '<p>refs</p>'
        self.item.responsible_organisation = 'My org'

        with reversion.create_revision():
            self.item.save()

        latest = reversion.models.Version.objects.get_for_object(self.item).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        names_and_refs = response.context['item']['item_data']['Names & References']
        self.assertFalse(names_and_refs['References'].is_link)
        self.assertTrue(names_and_refs['References'].is_html)
        self.assertEqual(names_and_refs['References'].value, '<p>refs</p>')

        self.assertFalse(names_and_refs['Responsible Organisation'].is_link)
        self.assertFalse(names_and_refs['Responsible Organisation'].is_html)
        self.assertEqual(names_and_refs['Responsible Organisation'].value, 'My org')

    @tag('item_app_check')
    def test_viewing_item_with_disabled_app(self):

        enabled_apps = ['aristotle_dse']
        with mock.patch('aristotle_mdr.views.views.fetch_metadata_apps', return_value=enabled_apps):
            self.login_editor()
            self.reverse_get(
                'aristotle:item',
                reverse_args=[self.item.id, 'objectclass', 'name'],
                status_code=404
            )

    @tag('item_app_check')
    def test_viewing_item_with_enabled_app(self):

        enabled_apps = ['aristotle_mdr']
        with mock.patch('aristotle_mdr.views.views.fetch_metadata_apps', return_value=enabled_apps):
            self.login_editor()
            self.reverse_get(
                'aristotle:item',
                reverse_args=[self.item.id, 'objectclass', 'name'],
                status_code=200
            )

    @tag('version')
    def test_version_workgroup_lookup(self):

        with reversion.create_revision():
            self.item.save()

        latest = reversion.models.Version.objects.get_for_object(self.item).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        workgroup = response.context['item']['workgroup']
        self.assertEqual(workgroup, self.wg1)

    @tag('version')
    def test_version_item_metadata(self):
        # Does this make it meta meta data

        with reversion.create_revision():
            self.item.save()

        latest = reversion.models.Version.objects.get_for_object(self.item).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        self.assertEqual(response.context['item']['id'], self.item.id)
        self.assertEqual(response.context['item']['pk'], self.item.id)
        self.assertEqual(response.context['item']['meta']['app_label'], 'aristotle_mdr')
        self.assertEqual(response.context['item']['meta']['model_name'], 'objectclass')
        self.assertEqual(response.context['item']['get_verbose_name'], 'Object Class')

    @tag('version')
    def test_view_non_concept_version(self):

        with reversion.create_revision():
            self.wg1.save()

        latest = reversion.models.Version.objects.get_for_object(self.wg1).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=404
        )

    @tag('version')
    def test_view_version_for_item_without_perm(self):

        with reversion.create_revision():
            item = models.ObjectClass.objects.create(
                name='cant view',
                definition='cant see this one',
                submitter=self.editor
            )

        latest = reversion.models.Version.objects.get_for_object(item).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=403
        )

    @tag('custfield')
    def test_submitter_can_save_via_edit_page_with_custom_fields(self):
        self.login_editor()
        cf = CustomField.objects.create(
            name='MyCustomField',
            type='int',
            help_text='Custom',
            order=0
        )

        postdata = utils.model_to_dict_with_change_time(self.item)
        postdata['custom_MyCustomField'] = 4
        response = self.reverse_post(
            'aristotle:edit_item',
            postdata,
            reverse_args=[self.item.id],
            status_code=302
        )
        self.item1 = models.ObjectClass.objects.get(pk=self.item.pk)
        self.assertRedirects(response, url_slugify_concept(self.item))

        cv_query = CustomValue.objects.filter(
            field=cf,
            concept=self.item1._concept_ptr
        )
        self.assertTrue(cv_query.count(), 1)
        cv = cv_query.first()
        self.assertEqual(cv.content, '4')

    @tag('custfield')
    def test_edit_page_custom_fields_initial(self):
        self.login_editor()
        cf = CustomField.objects.create(
            name='MyCustomField',
            type='int',
            help_text='Custom',
            order=0
        )
        cv = CustomValue.objects.create(
            field=cf,
            concept=self.item,
            content='4'
        )
        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.item.id],
            status_code=200
        )
        initial = response.context['form'].initial
        self.assertTrue('custom_MyCustomField' in initial)
        self.assertEqual(initial['custom_MyCustomField'], '4')

    def get_custom_values_for_user(self, user):
        """Util function used for the following 3 tests"""
        view = ConceptRenderView()
        request = self.factory.get('/anitemurl/')
        request.user = user
        view.request = request
        view.item = self.item
        return view.get_custom_values()

    @tag('custfield')
    def test_view_custom_values_unath(self):
        self.setup_custom_values()
        anon = AnonymousUser()
        cvs = self.get_custom_values_for_user(anon)
        self.assertEqual(len(cvs), 1)
        self.assertEqual(cvs[0].content, 'All Value')

    @tag('custfield')
    def test_view_custom_values_auth(self):
        self.setup_custom_values()
        cvs = self.get_custom_values_for_user(self.regular)
        self.assertEqual(len(cvs), 2)
        self.assertEqual(cvs[0].content, 'All Value')
        self.assertEqual(cvs[1].content, 'Auth Value')

    @tag('custfield')
    def test_view_custom_values_auth(self):
        self.setup_custom_values()
        cvs = self.get_custom_values_for_user(self.viewer)
        self.assertEqual(len(cvs), 3)
        self.assertEqual(cvs[0].content, 'All Value')
        self.assertEqual(cvs[1].content, 'Auth Value')
        self.assertEqual(cvs[2].content, 'Workgroup Value')


# These are run by all item types
class LoggedInViewConceptPages(utils.AristotleTestUtils):
    defaults = {}

    def setUp(self):
        super().setUp()

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

    # ---- utils ----

    def loadHelp(self):
        from django.core.management import call_command
        call_command('load_aristotle_help', verbosity=0, interactive=False)

    def update_defn_with_versions(self, new_defn='brand new definition'):
        with reversion.create_revision():
            self.item1.save()

        with reversion.create_revision():
            self.item1.definition = new_defn
            self.item1.save()

        item1_concept = self.item1._concept_ptr

        concept_versions = reversion.models.Version.objects.get_for_object(item1_concept)
        self.assertEqual(concept_versions.count(), 2)

        item_versions = reversion.models.Version.objects.get_for_object(self.item1)
        self.assertEqual(item_versions.count(), 2)

    # ---- tests ----

    def test_su_can_view(self):
        self.login_superuser()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        response = self.client.get(self.get_page(self.item2))
        self.assertEqual(response.status_code,200)

        # Ensure short urls redirect properly
        response = self.client.get(reverse("aristotle:item_short", args=[self.item1.pk]))
        self.assertEqual(response.status_code,302)

    def test_editor_can_view(self):
        self.login_editor()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        response = self.client.get(self.get_page(self.item2))
        self.assertEqual(response.status_code,403)

    def test_viewer_can_view(self):
        self.login_viewer()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        response = self.client.get(self.get_page(self.item2))
        self.assertEqual(response.status_code,403)

    def test_stubs_redirect_correctly(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:item',args=[self.item1.id]))
        self.assertRedirects(response,url_slugify_concept(self.item1))
        response = self.client.get(reverse('aristotle:item',args=[self.item1.id])+"/not-a-model/fake-name")
        self.assertRedirects(response,url_slugify_concept(self.item1))
        response = self.client.get(reverse('aristotle:item',args=[self.item1.id])+"/this-isnt-even-a-proper-stub")
        self.assertRedirects(response,url_slugify_concept(self.item1))

    def test_uuids_redirect_correctly(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:item_uuid',args=[self.item1.id]))
        self.assertRedirects(response,url_slugify_concept(self.item1))

    def test_anon_cannot_view_edit_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,302)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,302)
    def test_viewer_cannot_view_edit_page(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)
    def test_submitter_can_view_edit_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        form = response.context['form']
        self.assertTrue('change_comments' in form.fields)

        response = self.client.get(reverse('aristotle:edit_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_regular_can_view_own_items_edit_page(self):
        self.login_regular_user()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)
        self.regular_item = self.itemType.objects.create(name="regular item",definition="my definition", submitter=self.regular,**self.defaults)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.regular_item.id]))
        self.assertEqual(response.status_code,200)

    def test_regular_can_save_via_edit_page(self):
        self.login_regular_user()
        self.regular_item = self.itemType.objects.create(name="regular item",definition="my definition", submitter=self.regular,**self.defaults)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.regular_item.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        response = self.client.post(reverse('aristotle:edit_item',args=[self.regular_item.id]), updated_item)
        self.regular_item = self.itemType.objects.get(pk=self.regular_item.pk)
        self.assertRedirects(response,url_slugify_concept(self.regular_item))
        self.assertEqual(self.regular_item.name,updated_name)

    def test_submitter_can_save_via_edit_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.name,updated_name)

    def test_submitter_can_save_item_with_no_workgroup_via_edit_page(self):
        self.login_editor()
        self.item1 = self.itemType.objects.create(name="Test Item 1 (visible to tested viewers)",submitter=self.editor,definition="my definition",**self.defaults)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.name,updated_name)
        self.assertEqual(self.item1.workgroup,None)

    def test_submitter_can_save_via_edit_page_with_change_comment(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        change_comment = "I changed this because I can"
        updated_item['change_comments'] = change_comment
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.name,updated_name)

        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, change_comment)

        self.logout()
        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)
        # self.assertNotContains(response, change_comment)

        models.Status.objects.create(
            concept=self.item1,
            registrationAuthority=self.ra,
            registrationDate = datetime.date(2009,4,28),
            state =  models.STATES.standard
            )

        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1._is_public)
        self.assertTrue(self.item1.can_view(None))

        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)

        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        self.assertNotContains(response, change_comment)


    def test_submitter_can_save_via_edit_page_with_slots(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.slots.count(),0)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name

        formset_data = [
            {
                'concept': self.item1.pk,
                'name': 'extra',
                'type': 'string',
                'value': 'test slot value',
                'order': 0,
                'permission': 0,
            },
            {
                'concept': self.item1.pk,
                'name': 'more_extra',
                'type': 'string',
                'value': 'an even better test slot value',
                'order': 1,
                'permission': 0,
            }
        ]
        slot_formset_data = self.get_formset_postdata(formset_data, 'slots')

        updated_item.update(slot_formset_data)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.slots.count(),2)

        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertContains(response, 'test slot value')
        self.assertContains(response, 'an even better test slot value')

        slots = self.item1.slots.all()
        self.assertEqual(slots[0].name, 'extra')
        self.assertEqual(slots[0].order, 0)
        self.assertEqual(slots[1].name, 'more_extra')
        self.assertEqual(slots[1].order, 1)


    def test_submitter_can_save_via_edit_page_with_identifiers(self):

        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.slots.count(),0)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name

        namespace = ident_models.Namespace.objects.create(
            naming_authority=self.ra,
            shorthand_prefix='pre'
        )

        formset_data = [
            {
                'concept': self.item1.pk,
                'namespace': namespace.pk,
                'identifier': 'YE',
                'version': 1,
                'order': 0
            },
            {
                'concept': self.item1.pk,
                'namespace': namespace.pk,
                'identifier': 'RE',
                'version': 1,
                'order': 1
            }
        ]
        ident_formset_data = self.get_formset_postdata(formset_data, 'identifiers')

        updated_item.update(ident_formset_data)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.assertRedirects(response,url_slugify_concept(self.item1))
        self.assertEqual(self.item1.identifiers.count(),2)

        response = self.client.get(reverse('aristotle:item',args=[self.item1.id]), follow=True)
        self.assertContains(response, 'pre</a>/YE/1')
        self.assertContains(response, 'pre</a>/RE/1')

        idents = self.item1.identifiers.all()
        self.assertEqual(idents[0].identifier, 'YE')
        self.assertEqual(idents[0].order, 0)
        self.assertEqual(idents[1].identifier, 'RE')
        self.assertEqual(idents[1].order, 1)

    def test_submitter_cannot_save_via_edit_page_if_other_saves_made(self):
        from datetime import timedelta
        self.login_editor()
        modified = self.item1.modified
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        # fake that we fetched the page seconds before modification
        updated_item = utils.model_to_dict_with_change_time(response.context['item'],fetch_time=modified-timedelta(seconds=5))
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        change_comment = "I changed this because I can"
        updated_item['change_comments'] = change_comment
        time_before_response = timezone.now()
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)

        self.assertEqual(response.status_code,200)
        form = response.context['form']
        self.assertTrue(form.errors['last_fetched'][0] == CheckIfModifiedMixin.modified_since_form_fetched_error)

        # When sending a response with a bad last_fetch, the new one should come back right
        self.assertTrue(time_before_response < form.fields['last_fetched'].initial)

        # With the new last_fetched we can submit ok!
        updated_item['last_fetched'] = form.fields['last_fetched'].initial
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)


        updated_item.pop('last_fetched')
        time_before_response = timezone.now()
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)

        self.assertEqual(response.status_code,200)
        form = response.context['form']
        self.assertTrue(form.errors['last_fetched'][0] == CheckIfModifiedMixin.modified_since_field_missing)
        # When sending a response with no last_fetch, the new one should come back right
        self.assertTrue(time_before_response < form.fields['last_fetched'].initial)

        # With the new last_fetched we can submit ok!
        updated_item['last_fetched'] = form.fields['last_fetched'].initial
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)

    # Test if workgroup-moving settings work

    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=[]))
    def test_submitter_cannot_change_workgroup_via_edit_page(self):
        # based on the idea that 'submitter' is not set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")
        self.wg_other.submitters.add(self.editor)

        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])

        updated_item['workgroup'] = str(self.wg_other.pk)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']

        self.assertTrue('workgroup' in form.errors.keys())
        self.assertTrue(len(form.errors['workgroup'])==1)

        # Submitter is logged in, tries to move item - fails because
        self.assertFalse(perms.user_can_remove_from_workgroup(self.editor,self.item1.workgroup))
        self.assertTrue(form.errors['workgroup'][0] == WorkgroupVerificationMixin.cant_move_any_permission_error)

        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']

        self.assertTrue('workgroup' in form.errors.keys())
        self.assertTrue(len(form.errors['workgroup'])==1)

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=['submitter']))
    def test_submitter_can_change_workgroup_via_edit_page(self):
        # based on the idea that 'submitter' is set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")

        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_item['workgroup'] = str(self.wg_other.pk)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

        self.wg_other.submitters.add(self.editor)

        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)

        self.assertEqual(response.status_code,302)
        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])


    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=['admin']))
    def test_admin_can_change_workgroup_via_edit_page(self):
        # based on the idea that 'admin' is set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")

        self.login_superuser()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(self.item1)
        updated_item['workgroup'] = str(self.wg_other.pk)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)

        updated_item = utils.model_to_dict_with_change_time(self.item1)
        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)


    @override_settings(ARISTOTLE_SETTINGS=dict(settings.ARISTOTLE_SETTINGS, WORKGROUP_CHANGES=['manager']))
    def test_manager_of_two_workgroups_can_change_workgroup_via_edit_page(self):
        # based on the idea that 'manager' is set in ARISTOTLE_SETTINGS.WORKGROUP
        self.wg_other = models.Workgroup.objects.create(name="Test WG to move to")
        self.wg_other.submitters.add(self.editor)

        self.login_editor()
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_item['workgroup'] = str(self.wg_other.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']
        # Submitter can't move because they aren't a manager of any workgroups.
        self.assertTrue(form.errors['workgroup'][0] == WorkgroupVerificationMixin.cant_move_any_permission_error)

        self.wg_other.managers.add(self.editor)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        form = response.context['form']
        # Submitter can't move because they aren't a manager of the workgroup the item is in.
        self.assertTrue(form.errors['workgroup'][0] == WorkgroupVerificationMixin.cant_move_from_permission_error)


        self.login_manager()

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,403)

        self.wg1.submitters.add(self.manager) # Need to give manager edit permission to allow them to actually edit things
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)
        form = response.context['form']

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

        self.wg_other.managers.add(self.manager)

        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)
        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

        self.wg_other.submitters.add(self.manager) # Need to give manager edit permission to allow them to actually edit things
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,302)

        updated_item['workgroup'] = str(self.wg2.pk)
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.assertEqual(response.status_code,200)

        self.assertTrue('Select a valid choice.' in form.errors['workgroup'][0])

    def test_anon_cannot_view_clone_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,302)
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,302)

    def test_viewer_can_view_clone_page(self):
        self.login_viewer()
        # Viewer can clone an item they can see
        self.assertTrue(perms.user_can_view(self.viewer, self.item1))
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        # Viewer can't clone an item they can't see
        self.assertFalse(perms.user_can_view(self.viewer, self.item2))
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_submitter_can_view_clone_page(self):
        self.login_editor()
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_submitter_can_save_via_clone_page(self):
        self.login_editor()
        import time
        time.sleep(2) # delays so there is a definite time difference between the first item and the clone on very fast test machines
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict(response.context['item'])
        updated_name = updated_item['name'] + " cloned!"
        updated_item['name'] = updated_name
        response = self.client.post(reverse('aristotle:clone_item',args=[self.item1.id]), updated_item)
        most_recent = self.itemType.objects.order_by('-created').first()
        self.assertTrue(perms.user_can_view(self.editor, most_recent))

        self.assertRedirects(response,url_slugify_concept(most_recent))
        self.assertEqual(most_recent.name,updated_name)

        # Make sure the right item was save and our original hasn't been altered.
        self.item1 = self.itemType.objects.get(id=self.item1.id) # Stupid cache
        self.assertTrue('cloned' not in self.item1.name)

    def test_submitter_can_save_via_clone_page_with_no_workgroup(self):
        self.login_editor()
        import time
        time.sleep(2) # delays so there is a definite time difference between the first item and the clone on very fast test machines
        response = self.client.get(reverse('aristotle:clone_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict(response.context['item'])
        updated_name = updated_item['name'] + " cloned with no WG!"
        updated_item['name'] = updated_name
        updated_item['workgroup'] = '' # no workgroup this time
        response = self.client.post(reverse('aristotle:clone_item',args=[self.item1.id]), updated_item)

        self.assertTrue(response.status_code == 302) # make sure its saved ok
        most_recent = self.itemType.objects.order_by('-created').first()

        self.assertTrue('cloned with no WG' in most_recent.name)
        self.assertTrue(most_recent.workgroup == None)
        self.assertTrue(perms.user_can_view(self.editor, most_recent))

        self.assertRedirects(response,url_slugify_concept(most_recent))
        self.assertEqual(most_recent.name,updated_name)

        # Make sure the right item was save and our original hasn't been altered.
        self.item1 = self.itemType.objects.get(id=self.item1.id) # Stupid cache
        self.assertTrue('cloned with no WG' not in self.item1.name)

    def test_help_page_exists(self):
        self.logout()
        self.loadHelp()
        response = self.client.get(
            reverse('aristotle_help:concept_help',args=[self.itemType._meta.app_label,self.itemType._meta.model_name])
        )
        self.assertEqual(response.status_code,200)

    def test_viewer_can_view_registration_history(self):
        self.login_viewer()
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

    def test_anon_cannot_view_registration_history(self):
        self.logout()
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item1.id]))
        self.assertEqual(response.status_code,302)
        response = self.client.get(reverse('aristotle:registrationHistory',args=[self.item2.id]))
        self.assertEqual(response.status_code,302)

    def test_viewer_can_view_item_history(self):
        # Workgroup members can see the edit history of items
        self.login_viewer()
        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        response = self.client.get(reverse('aristotle:item_history',args=[self.item2.id]))
        self.assertEqual(response.status_code,403)

        # # Viewers shouldn't even have the link to history on items they arent in the workgroup for
        # This check makes no sense - a user can't see the page to begin with.
        # Keeping for posterity
        # response = self.client.get(self.item2.get_absolute_url())
        # self.assertNotContains(response, reverse('aristotle:item_history',args=[self.item2.id]))

        # Viewers will even have the link to history on items they are in the workgroup for
        response = self.client.get(self.item1.get_absolute_url())
        self.assertContains(response, reverse('aristotle:item_history',args=[self.item1.id]))

    def test_editor_can_view_item_history__and__compare(self):
        self.login_editor()

        #from reversion import revisions as reversion
        import reversion

        with reversion.revisions.create_revision():
            self.item1.name = "change 1"
            reversion.set_comment("change 1")
            self.item1.save()

        self.make_review_request(self.item1, self.registrar)

        with reversion.revisions.create_revision():
            self.item1.name = "change 2"
            reversion.set_comment("change 2")
            self.ra.register(
                item=self.item1,
                state=models.STATES.incomplete,
                user=self.registrar
            )
            self.item1.save()

        from reversion.models import Version
        revisions = Version.objects.get_for_object(self.item1)

        response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        response = self.client.get(
            reverse('aristotle:item_history',args=[self.item1.id]),
            {'version_id1' : revisions.first().pk,
            'version_id2' : revisions.last().pk
            }
        )

        self.assertEqual(response.status_code,200)
        self.assertContains(response, "change 2")
        self.assertContains(response, 'statuses')

        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache
        self.assertTrue(self.item1.name == "change 2")
        for s in self.item1.statuses.all():
            self.assertContains(
                response,
                '%s is %s'%(self.item1.name,s.get_state_display())
            )

    def test_editor_can_revert_item_and_status_goes_back_too(self):
        self.login_editor()

        # REVISION 0
        import reversion
        #from reversion import revisions as reversion
        with reversion.revisions.create_revision():
            self.item1.save()
        original_name = self.item1.name

        # REVISION 1
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name
        change_comment = "I changed this because I can"
        updated_item['change_comments'] = change_comment

        # REVISION 2
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.name,updated_name)

        self.make_review_request(self.item1, self.registrar)

        self.ra.register(
            item=self.item1,
            state=models.STATES.incomplete,
            user=self.registrar
        )
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache

        self.assertTrue(self.item1.statuses.all().count() == 1)
        self.assertTrue(self.item1.statuses.first().state == models.STATES.incomplete)

        # REVISION 3
        response = self.client.get(reverse('aristotle:edit_item',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name_again = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name_again
        change_comment = "I changed this again because I can"
        updated_item['change_comments'] = change_comment

        # REVISION 4
        response = self.client.post(reverse('aristotle:edit_item',args=[self.item1.id]), updated_item)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.name,updated_name_again)

        # REVISION 5
        self.ra.register(self.item1,models.STATES.candidate,self.registrar)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache
        self.assertTrue(self.item1.statuses.count() == 2)
        self.assertTrue(self.item1.statuses.last().state == models.STATES.candidate)

        from django.contrib.contenttypes.models import ContentType
        ct = ContentType.objects.get_for_model(self.item1._meta.model)
        versions = list(
            reversion.models.Version.objects.filter(
                object_id=self.item1.id,
                content_type_id=ct.id
            ).order_by('revision__date_created')
        )
        versions[2].revision.revert(delete=True) # The version that has the first status changes

        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache

        self.assertTrue(self.item1.statuses.count() == 1)
        self.assertTrue(self.item1.statuses.first().state == models.STATES.incomplete)
        self.assertEqual(self.item1.name,updated_name)

        # Go back to the initial revision
        versions[0].revision.revert(delete=True)
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache
        self.assertTrue(self.item1.statuses.count() == 0)
        self.assertEqual(self.item1.name,original_name)


        versions[4].revision.revert(delete=True) # Back to the latest version
        self.item1 = self.itemType.objects.get(pk=self.item1.pk) #decache

        self.assertTrue(self.item1.statuses.count() == 2)
        self.assertTrue(self.item1.statuses.order_by('state')[0].state == models.STATES.incomplete)
        self.assertTrue(self.item1.statuses.order_by('state')[1].state == models.STATES.candidate)
        self.assertEqual(self.item1.name,updated_name_again)


    # def test_anon_cannot_view_item_history(self):
    #     self.logout()
    #     response = self.client.get(reverse('aristotle:item_history',args=[self.item1.id]))
    #     self.assertEqual(response.status_code,302)
    #     response = self.client.get(reverse('aristotle:item_history',args=[self.item2.id]))
    #     self.assertEqual(response.status_code,302)


    #     # Register to check if link is on page... it shouldn't be
    #     models.Status.objects.create(
    #         concept=self.item1,
    #         registrationAuthority=self.ra,
    #         registrationDate = datetime.date(2009,4,28),
    #         state =  models.STATES.standard
    #         )

    #     # Anon users shouldn't even have the link to history *any* items
    #     response = self.client.get(self.item1.get_absolute_url())
    #     self.assertEqual(response.status_code,200)
    #     self.assertNotContains(response, reverse('aristotle:item_history',args=[self.item1.id]))

    @tag('changestatus')
    def test_registrar_can_change_status(self):
        self.login_registrar()

        self.make_review_request(self.item1, self.registrar)

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'change_status-registrationAuthorities': [str(self.ra.id)],
                'change_status-state': self.ra.public_state,
                'change_status-changeDetails': "testing",
                'change_status-cascadeRegistration': 0, # no
                'submit_skip': 'value',
                'change_status_view-current_step': 'change_status',
            }
        )
        self.assertRedirects(response,url_slugify_concept(self.item1))

        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.statuses.count(),1)
        self.assertTrue(self.item1.is_registered)
        self.assertTrue(self.item1.is_public())

    @tag('inactive_ra', 'changestatus')
    def test_registrar_cant_change_status_with_inactive_ra(self):

        self.login_registrar()
        self.make_review_request(self.item1, self.registrar)

        # Deactivate RA
        self.ra.active = 1
        self.ra.save()

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)
        self.assertFalse(self.ra in response.context['form'].fields['registrationAuthorities'].queryset)

        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'change_status-registrationAuthorities': [str(self.ra.id)],
                'change_status-state': self.ra.public_state,
                'change_status-changeDetails': "testing",
                'change_status-cascadeRegistration': 0, # no
                'submit_skip': 'value',
                'change_status_view-current_step': 'change_status',
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('registrationAuthorities' in response.context['form'].errors)


    @tag('changestatus')
    def test_registrar_can_change_status_with_cascade(self):
        if not hasattr(self,"run_cascade_tests"):
            return
        self.login_registrar()

        self.make_review_request(self.item1, self.registrar)

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        for sub_item in self.item1.registry_cascade_items:
            if sub_item is not None:
                self.assertEqual(sub_item.statuses.count(),0)
            else:
                pass

        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'change_status-registrationAuthorities': [str(self.ra.id)],
                'change_status-state': self.ra.public_state,
                'change_status-changeDetails': "testing",
                'change_status-cascadeRegistration': 1, # yes
                'submit_skip': 'value',
                'change_status_view-current_step': 'change_status',
            }
        )
        self.assertRedirects(response,url_slugify_concept(self.item1))

        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.statuses.count(),1)
        self.assertTrue(self.item1.is_registered)
        self.assertTrue(self.item1.is_public())
        for sub_item in self.item1.registry_cascade_items:
            if sub_item is not None:
                if not sub_item.is_registered: # pragma: no cover
                    # This is debug code, and should never happen
                    print(sub_item)
                self.assertTrue(sub_item.is_registered)

    @tag('changestatus')
    def test_registrar_cannot_use_faulty_statuses(self):
        self.login_registrar()

        self.assertFalse(perms.user_can_view(self.registrar,self.item1))
        self.item1.save()
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        self.make_review_request(self.item1, self.registrar)

        self.assertTrue(perms.user_can_view(self.registrar,self.item1))
        self.assertTrue(perms.user_can_change_status(self.registrar,self.item1))

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        response = self.client.post(
            reverse('aristotle:changeStatus', args=[self.item1.id]),
            {
                'change_status-registrationAuthorities': [str(self.ra.id)],
                'change_status-state': "Not a number", # obviously wrong
                'change_status-changeDetails': "testing",
                'change_status-cascadeRegistration': 0, # no
                'submit_skip': 'value',
                'change_status_view-current_step': 'change_status',
            }
        )
        self.assertFormError(response, 'form', 'state', 'Select a valid choice. Not a number is not one of the available choices.')

        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'change_status-registrationAuthorities': [str(self.ra.id)],
                'change_status-state': "343434", # also wrong
                'change_status-changeDetails': "testing",
                'change_status-cascadeRegistration': 0, # no
                'submit_skip': 'value',
                'change_status_view-current_step': 'change_status',
            }
        )
        self.assertFormError(response, 'form', 'state', 'Select a valid choice. 343434 is not one of the available choices.')

    def registrar_can_change_status_with_review(self, cascade, check_bad_perms=False):
        if not hasattr(self,"run_cascade_tests") and cascade:
            return
        self.login_registrar()

        self.assertFalse(perms.user_can_view(self.registrar,self.item1))
        self.item1.save()
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)

        review = self.make_review_request(self.item1, self.registrar)

        self.assertTrue(perms.user_can_view(self.registrar,self.item1))
        self.assertTrue(perms.user_can_change_status(self.registrar,self.item1))

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,200)

        self.assertEqual(self.item1.statuses.count(),0)
        for sub_item in self.item1.registry_cascade_items:
            if sub_item is not None:
                self.assertEqual(sub_item.statuses.count(),0)
            else:
                pass

        if cascade:
            cascade_post = 1
            if not check_bad_perms:
                # add all cascade items to review
                for item in self.item1.registry_cascade_items:
                    review.concepts.add(item)
        else:
            cascade_post = 0

        response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'change_status-registrationAuthorities': [str(self.ra.id)],
                'change_status-state': self.ra.public_state,
                'change_status-changeDetails': "testing",
                'change_status-cascadeRegistration': cascade_post,
                'submit_next': 'value',
                'change_status_view-current_step': 'change_status',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['wizard']['steps'].step1, 2) # check we are now on second setep
        selected_for_change = [self.item1.id]

        if cascade:
            selected_for_change.append(self.item1.registry_cascade_items[0].id)

        selected_for_change_strings = [str(a) for a in selected_for_change]

        review_response = self.client.post(
            reverse('aristotle:changeStatus',args=[self.item1.id]),
            {
                'review_changes-selected_list': selected_for_change_strings,
                'change_status_view-current_step': 'review_changes',
            }
        )
        self.assertRedirects(review_response,url_slugify_concept(self.item1))

        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertEqual(self.item1.statuses.count(),1)
        self.assertTrue(self.item1.is_registered)
        self.assertTrue(self.item1.is_public())
        if cascade:
            for sub_item in self.item1.registry_cascade_items:
                if sub_item is not None:
                    if sub_item.id in selected_for_change:
                        if not check_bad_perms:
                            self.assertTrue(sub_item.is_registered)
                        else:
                            self.assertFalse(sub_item.is_registered)
                    else:
                        self.assertFalse(sub_item.is_registered)

    @tag('changestatus')
    def test_registrar_can_change_status_with_review_cascade(self):
        self.registrar_can_change_status_with_review(cascade=True)

    @tag('changestatus')
    def test_registrar_cant_update_cascaded_items_without_perm(self):
        self.registrar_can_change_status_with_review(cascade=True, check_bad_perms=True)

    @tag('changestatus')
    def test_registrar_can_change_status_with_review_no_cascade(self):
        self.registrar_can_change_status_with_review(cascade=False)

    @tag('changestatus')
    def test_viewer_cannot_change_status(self):
        self.login_viewer()

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertEqual(response.status_code,403)

    @tag('changestatus')
    def test_anon_cannot_change_status(self):
        self.logout()

        response = self.client.get(reverse('aristotle:changeStatus',args=[self.item1.id]))
        self.assertRedirects(response,reverse('friendly_login')+"?next="+reverse('aristotle:changeStatus', args=[self.item1.id]))

    @tag('changestatus')
    def test_cascade_action(self):
        self.logout()
        check_url = reverse('aristotle:check_cascaded_states', args=[self.item1.pk])

        response = self.client.get(check_url)
        self.assertEqual(response.status_code,403)

        self.login_editor()

        response = self.client.get(check_url)
        self.assertEqual(response.status_code,404)

    def test_weak_editing_in_advanced_editor_dynamic(self, updating_field=None, default_fields={}):

        if hasattr(self.item1, 'serialize_weak_entities'):
            self.login_editor()
            value_url = 'aristotle:edit_item'

            response = self.client.get(reverse(value_url,args=[self.item1.id]))
            self.assertEqual(response.status_code, 200)

            weak_formsets = response.context['weak_formsets']

            weak = self.item1.serialize_weak_entities

            for entity in weak:

                value_type = entity[1]
                pre = entity[0]

                # find associated formset
                current_formset = None
                for formset in weak_formsets:
                    if formset['formset'].prefix == pre:
                        current_formset = formset['formset']

                # check that a formset with the correct prefix was rendered
                self.assertIsNotNone(current_formset)

                data = utils.model_to_dict_with_change_time(self.item1)

                num_vals = getattr(self.item1,value_type).all().count()
                ordering_field = getattr(self.item1,value_type).model.ordering_field

                # check to make sure the classes with weak entities added them on setUp below
                self.assertGreater(num_vals, 0)

                skipped_fields = ['id', 'ORDER', 'start_date', 'end_date', 'DELETE']
                for i,v in enumerate(getattr(self.item1,value_type).all()):
                    data.update({"%s-%d-id"%(pre,i): v.pk, "%s-%d-ORDER"%(pre,i) : getattr(v, ordering_field)})
                    for field in current_formset[0].fields:
                        if hasattr(v, field) and field not in skipped_fields:
                            value = getattr(v, field)
                            if value is not None:

                                if (updating_field is None):
                                    # see if this is the field to update
                                    model_field = current_formset[0]._meta.model._meta.get_field(field)

                                    if isinstance(model_field, CharField) or isinstance(model_field, TextField):
                                        updating_field = field

                                if field == updating_field:
                                    data.update({"%s-%d-%s"%(pre,i,field) : value + ' -updated'})
                                else:
                                    added_value = value
                                    if field in default_fields:
                                        data.update({"%s-%d-%s"%(pre,i,field) : default_fields[field]})
                                        added_value = default_fields[field]
                                    else:
                                        data.update({"%s-%d-%s"%(pre,i,field) : value})
                                    if (i == num_vals - 1):
                                        # add a copy
                                        data.update({"%s-%d-%s"%(pre,i+1,field) : added_value})

                self.assertIsNotNone(updating_field)
                # no string was found to update
                # if this happends the test needs to be passed an updating_field or changed to support more than text updates

                i=0
                data.update({"%s-%d-DELETE"%(pre,i): 'checked', "%s-%d-%s"%(pre,i,updating_field) : getattr(v, updating_field)+" - deleted"}) # delete the last one.

                # add order and updating_value to newly added data
                i=num_vals
                data.update({"%s-%d-ORDER"%(pre,i) : i, "%s-%d-%s"%(pre,i,updating_field) : "new value -updated"})

                # add management form
                data.update({
                    "%s-TOTAL_FORMS"%pre:num_vals+1, "%s-INITIAL_FORMS"%pre: num_vals, "%s-MAX_NUM_FORMS"%pre:1000,
                    })

                response = self.client.post(reverse(value_url,args=[self.item1.id]), data)

                self.item1 = self.itemType.objects.get(pk=self.item1.pk)

                self.assertTrue(num_vals == getattr(self.item1,value_type).all().count())

                new_value_seen = False
                for v in getattr(self.item1,value_type).all():
                    value = getattr(v, updating_field)
                    self.assertTrue('updated' in value) # This will fail if the item isn't updated
                    self.assertFalse('deleted' in value) # make sure deleted value not present
                    if value == 'new value -updated':
                        new_value_seen = True
                self.assertTrue(new_value_seen)

    @tag('version')
    def test_view_previous_version_from_concept(self):
        old_definition = self.item1.definition

        self.update_defn_with_versions()

        item1_concept = self.item1._concept_ptr
        versions = reversion.models.Version.objects.get_for_object(item1_concept)
        self.assertEqual(versions.count(), 2)
        oldest_version = versions.last()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[oldest_version.id],
            status_code=200
        )

        item_context = response.context['item']
        self.assertEqual(item_context['definition'], old_definition)

    @tag('version')
    def test_view_previous_version_from_item_version(self):

        old_definition = self.item1.definition

        self.update_defn_with_versions()

        versions = reversion.models.Version.objects.get_for_object(self.item1)
        self.assertEqual(versions.count(), 2)
        oldest_version = versions.last()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[oldest_version.id],
            status_code=200
        )

        item_context = response.context['item']
        self.assertEqual(item_context['definition'], old_definition)

    @tag('download')
    @override_settings(ARISTOTLE_SETTINGS={'DOWNLOADERS': ['aristotle_mdr.downloaders.HTMLDownloader']})
    def test_download_content(self):
        downloader = HTMLDownloader([self.item1.id], self.editor.id, {})
        html = downloader.get_html().decode()
        self.assertTrue(len(html) > 0)
        self.assertTrue(self.item1.definition in html)


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
        super().setUp()

        for i in range(4):
            models.PermissibleValue.objects.create(
                value=i,meaning="test permissible meaning %d"%i,order=i,valueDomain=self.item1
            )
        for i in range(4):
            models.SupplementaryValue.objects.create(
                value=i,meaning="test supplementary meaning %d"%i,order=i,valueDomain=self.item1
            )

        # Data used to test value domain conceptual domain link
        cd = models.ConceptualDomain.objects.create(
            description='test description'
        )

        cd2 = models.ConceptualDomain.objects.create(
            description='unrelated conceptual domain'
        )
        models.ValueMeaning.objects.create(
            name="test name",
            definition="test definition",
            conceptual_domain=cd2,
            order=0,
        )

        self.vms = []
        for i in range(2):
            vm = models.ValueMeaning.objects.create(
                name="test name",
                definition="test definition",
                conceptual_domain=cd,
                order=i,
            )
            self.vms.append(vm)

        self.item3.conceptual_domain = cd
        self.item3.save()

    def test_weak_editing_in_advanced_editor_dynamic(self):
        super().test_weak_editing_in_advanced_editor_dynamic(updating_field='value')

    def test_anon_cannot_use_value_page(self):
        self.logout()
        response = self.client.get(reverse('aristotle:permsissible_values_edit',args=[self.item1.id]))
        self.assertRedirects(response,reverse('friendly_login')+"?next="+reverse('aristotle:permsissible_values_edit',args=[self.item1.id]))
        response = self.client.get(reverse('aristotle:supplementary_values_edit',args=[self.item1.id]))
        self.assertRedirects(response,reverse('friendly_login')+"?next="+reverse('aristotle:supplementary_values_edit',args=[self.item1.id]))

    def loggedin_user_can_use_value_page(self,value_url,current_item,http_code):
        response = self.client.get(reverse(value_url,args=[current_item.id]))
        self.assertEqual(response.status_code,http_code)

    def submitter_user_can_use_value_edit_page(self,value_type):
        value_url = {
            'permissible': 'aristotle:permsissible_values_edit',
            'supplementary': 'aristotle:supplementary_values_edit'
        }.get(value_type)

        self.login_editor()
        self.loggedin_user_can_use_value_page(value_url,self.item1,200)
        self.loggedin_user_can_use_value_page(value_url,self.item2,403)
        self.loggedin_user_can_use_value_page(value_url,self.item3,200)

        data = {}
        num_vals = getattr(self.item1,value_type+"Values").count()
        i=0
        for i,v in enumerate(getattr(self.item1,value_type+"Values").all()):
            data.update({
                "%svalue_set-%d-valueDomain"%(value_type, i): self.item1.pk,
                "%svalue_set-%d-id"%(value_type,i): v.pk,
                "%svalue_set-%d-ORDER"%(value_type,i) : v.order,
                "%svalue_set-%d-value"%(value_type,i) : v.value,
                "%svalue_set-%d-meaning"%(value_type,i) : v.meaning+" -updated"
            })
        data.update({
            "%svalue_set-%d-DELETE"%(value_type,i): 'checked',
            "%svalue_set-%d-meaning"%(value_type,i) : v.meaning+" - deleted",
            "%svalue_set-%d-valueDomain"%(value_type, i): self.item1.pk,
        }) # delete the last one.
        # now add a new one
        i=i+1
        data.update({
            "%svalue_set-%d-ORDER"%(value_type,i) : i,
            "%svalue_set-%d-value"%(value_type,i) : 100,
            "%svalue_set-%d-meaning"%(value_type,i) : "new value (also an updated value)",
            "%svalue_set-%d-valueDomain"%(value_type, i): self.item1.pk,
        })

        data.update({
            "%svalue_set-TOTAL_FORMS"%(value_type): i+1,
            "%svalue_set-INITIAL_FORMS"%(value_type): num_vals,
            "%svalue_set-MAX_NUM_FORMS"%(value_type):1000,
        })

        response = self.client.post(reverse(value_url,args=[self.item1.id]),data)
        self.assertEqual(response.status_code, 302)
        self.item1 = models.ValueDomain.objects.get(pk=self.item1.pk)

        self.assertEqual(num_vals, getattr(self.item1,value_type+"Values").count())
        new_value_seen = False
        for v in getattr(self.item1,value_type+"Values").all():
            self.assertTrue('updated' in v.meaning) # This will fail if the deleted item isn't deleted
            if v.value == '100' and "new value" in v.meaning:
                new_value_seen = True
        self.assertTrue(new_value_seen)


        # Item is now locked, submitter is no longer able to edit
        models.Status.objects.create(
                concept=self.item1,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=self.ra.locked_state
                )

        self.item1 = models.ValueDomain.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1.is_locked())
        self.assertFalse(perms.user_can_edit(self.editor,self.item1))
        self.loggedin_user_can_use_value_page(value_url,self.item1,403)

    def test_submitter_can_use_permissible_value_edit_page(self):
        self.submitter_user_can_use_value_edit_page('permissible')

    def test_submitter_can_use_supplementary_value_edit_page(self):
        self.submitter_user_can_use_value_edit_page('supplementary')

    def test_submitter_user_doesnt_save_all_blank_permissible_value_edit_page(self):
        self.submitter_user_doesnt_save_all_blank('permissible')

    def test_submitter_user_doesnt_save_all_blank_supplementary_value_edit_page(self):
        self.submitter_user_doesnt_save_all_blank('supplementary')

    def submitter_user_doesnt_save_all_blank(self,value_type):
        value_url = {
            'permissible': 'aristotle:permsissible_values_edit',
            'supplementary': 'aristotle:supplementary_values_edit'
        }.get(value_type)

        self.login_editor()
        self.loggedin_user_can_use_value_page(value_url,self.item1,200)

        data = {}
        num_vals = getattr(self.item1,value_type+"Values").count()

        i=0
        for i,v in enumerate(getattr(self.item1,value_type+"Values").all()):
            data.update({
                "%svalue_set-%d-valueDomain"%(value_type, i): self.item1.pk,
                "%svalue_set-%d-id"%(value_type, i): v.pk,
                "%svalue_set-%d-ORDER"%(value_type, i) : v.order,
                "%svalue_set-%d-value"%(value_type, i) : v.value,
                "%svalue_set-%d-meaning"%(value_type, i) : v.meaning+" -updated"
            })

        # now add two new values that are all blank
        i=i+1
        data.update({"%svalue_set-%d-ORDER"%(value_type, i) : i, "%svalue_set-%d-value"%(value_type, i) : '', "%svalue_set-%d-meaning"%(value_type, i) : ""})
        i=i+1
        data.update({"%svalue_set-%d-ORDER"%(value_type, i) : i, "%svalue_set-%d-value"%(value_type, i) : '', "%svalue_set-%d-meaning"%(value_type, i) : ""})

        data.update({
            "%svalue_set-TOTAL_FORMS"%(value_type): i+1,
            "%svalue_set-INITIAL_FORMS"%(value_type): num_vals,
            "%svalue_set-MAX_NUM_FORMS"%(value_type):1000,
        })
        self.client.post(reverse(value_url,args=[self.item1.id]),data)
        self.item1 = models.ValueDomain.objects.get(pk=self.item1.pk)

        self.assertTrue(num_vals == getattr(self.item1,value_type+"Values").count())

    def test_values_shown_on_page(self):
        self.login_viewer()

        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)
        for pv in self.item1.permissiblevalue_set.all():
            self.assertContains(response,pv.meaning,1)
        for sv in self.item1.supplementaryvalue_set.all():
            self.assertContains(response,sv.meaning,1)

    def test_conceptual_domain_selection(self):
        self.login_editor()
        url = 'aristotle:permsissible_values_edit'
        self.loggedin_user_can_use_value_page(url,self.item3,200)

        response = self.client.get(reverse(url,args=[self.item3.id]))
        self.assertEqual(response.status_code, 200)

        # check queryset correctly filled from conceptual domain for item 2
        formset = response.context['formset']
        for form in formset:
            self.assertFalse('meaning' in form.fields)
            self.assertTrue('value_meaning' in form.fields)
            queryset = form.fields['value_meaning'].queryset
            for item in queryset:
                self.assertTrue(item in self.vms)

        # Check empty queryset for item 1 (no cd linked)
        response = self.client.get(reverse(url,args=[self.item1.id]))
        self.assertEqual(response.status_code, 200)

        formset = response.context['formset']
        for form in formset:
            self.assertFalse('value_meaning' in form.fields)
            self.assertTrue('meaning' in form.fields)

    @tag('version')
    def test_version_display_of_values(self):
        self.update_defn_with_versions()

        latest = reversion.models.Version.objects.get_for_object(self.item1).last()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        item_context = response.context['item']

        self.assertEqual(len(item_context['weak']), 2)

        # Check supplementary values are being displayed
        supp_values = item_context['weak'][0]
        self.assertEqual(supp_values['model'], 'Supplementary Value')

        meaning_ht = models.AbstractValue._meta.get_field('meaning').help_text

        self.assertEqual(len(supp_values['headers']), 6)
        self.assertFalse('Value Domain' in supp_values['headers'])
        self.assertEqual(len(supp_values['items']), 4)
        self.assertEqual(supp_values['items'][0]['Meaning'].value, 'test supplementary meaning 3')
        self.assertEqual(supp_values['items'][0]['Meaning'].help_text, meaning_ht)
        self.assertEqual(supp_values['items'][0]['Meaning'].is_link, False)

        # Check permissible values are being displayed
        perm_values = item_context['weak'][1]
        self.assertEqual(perm_values['model'], 'Permissible Value')

        self.assertEqual(len(perm_values['headers']), 6)
        self.assertFalse('Value Domain' in perm_values['headers'])
        self.assertEqual(len(perm_values['items']), 4)
        self.assertEqual(perm_values['items'][0]['Meaning'].value, 'test permissible meaning 3')
        self.assertEqual(perm_values['items'][0]['Meaning'].help_text, meaning_ht)
        self.assertEqual(perm_values['items'][0]['Meaning'].is_link, False)

    @tag('version')
    def test_version_display_of_value_meanings(self):

        vm = self.vms[0]

        models.PermissibleValue.objects.create(
            value='1',
            value_meaning=vm,
            order=0,
            valueDomain=self.item3
        )

        with reversion.create_revision():
            self.item3.save()

        latest = reversion.models.Version.objects.get_for_object(self.item3).last()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        weak_context = response.context['item']['weak']
        perm_values = weak_context[0]['items']

        self.assertEqual(weak_context[0]['model'], 'Permissible Value')

        self.assertTrue(perm_values[0]['Value Meaning'].is_link)
        self.assertEqual(perm_values[0]['Value Meaning'].obj, vm)
        self.assertEqual(perm_values[0]['Value Meaning'].link_id, self.item3.conceptual_domain.id)

    @tag('clone')
    def test_clone_vd_with_components(self):
        self.login_editor()
        data = {
            'name': 'Goodness (clone)',
            'definition': 'A measure of good'
        }

        response = self.reverse_post(
            'aristotle:clone_item',
            data,
            reverse_args=[self.item1.id],
            status_code=302
        )

        clone = models.ValueDomain.objects.get(name='Goodness (clone)')
        self.assertEqual(clone.permissiblevalue_set.count(), 4)
        self.assertEqual(clone.supplementaryvalue_set.count(), 4)

    def post_and_time_permissible_values(self, vd, data, datalist, initial):
        permdata = self.get_formset_postdata(datalist, 'permissible_values', initial)
        data.update(permdata)

        self.login_editor()
        self.start_timer()
        response = self.client.post(
            reverse('aristotle:edit_item', args=[vd.id]),
            data
        )
        self.end_timer()
        self.assertEqual(response.status_code, 302)
        vd = models.ValueDomain.objects.get(id=vd.id)
        self.assertEqual(vd.permissiblevalue_set.count(), 100)

    @tag('bulk_values')
    def test_create_bulk_values(self):
        vd = models.ValueDomain.objects.create(
            name='Lots of values',
            definition='Lots',
            submitter=self.editor
        )
        data = utils.model_to_dict_with_change_time(vd)

        datalist = []
        for i in range(100):
            datalist.append({
                'value': 'Value {}'.format(i),
                'meaning': 'Meaning {}'.format(i),
                'valueDomain': vd.id,
                'ORDER': i
            })

        self.post_and_time_permissible_values(vd, data, datalist, 0)

    @tag('bulk_values')
    def test_reorder_bulk_values(self):
        vd = models.ValueDomain.objects.create(
            name='Lots of values',
            definition='Lots',
            submitter=self.editor
        )
        data = utils.model_to_dict_with_change_time(vd)

        datalist = []
        for i in range(100):
            value='Value {}'.format(i),
            meaning='Meaning {}'.format(i),
            pv = models.PermissibleValue.objects.create(
                valueDomain=vd,
                value=value,
                meaning=meaning,
                order=i
            )
            datalist.append({
                'id': pv.id,
                'value': value,
                'meaning': meaning,
                'valueDomain': vd.id,
                'ORDER': i + 1
            })

        self.post_and_time_permissible_values(vd, data, datalist, 100)


class ConceptualDomainViewPage(LoggedInViewConceptPages, TestCase):
    url_name='conceptualDomain'
    itemType=models.ConceptualDomain

    def setUp(self):
        super().setUp()

        for i in range(4):
            models.ValueMeaning.objects.create(
                name="test name",
                definition="test definition",
                conceptual_domain=self.item1,
                order=i,
            )

    @tag('edit_formsets')
    def test_edit_formset_error_display(self):

        self.login_editor()

        edit_url = 'aristotle:edit_item'
        response = self.client.get(reverse(edit_url,args=[self.item1.id]))
        self.assertEqual(response.status_code, 200)

        data = utils.model_to_dict_with_change_time(self.item1)

        # submit an item with a blank name
        valuemeaning_formset_data = [
            {'name': '', 'definition': 'test defn', 'start_date': '1999-01-01', 'end_date': '2090-01-01', 'ORDER': 0},
            {'name': 'Test2', 'definition': 'test defn', 'start_date': '1999-01-01', 'end_date': '2090-01-01', 'ORDER': 1}
        ]
        data.update(self.get_formset_postdata(valuemeaning_formset_data, 'value_meaning', 0))
        response = self.client.post(reverse(edit_url,args=[self.item1.id]), data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['weak_formsets'][0]['formset'].errors[0], {'name': ['This field is required.']})
        self.assertContains(response, 'This field is required.')


class DataElementConceptViewPage(LoggedInViewConceptPages, TestCase):
    url_name='dataElementConcept'
    itemType=models.DataElementConcept
    run_cascade_tests = True

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
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

    def test_foreign_key_popups(self):
        self.logout()

        check_url = reverse('aristotle:generic_foreign_key_editor', args=[self.item1.pk, 'objectclassarino'])
        response = self.client.get(check_url)
        self.assertEqual(response.status_code,404)

        check_url = reverse('aristotle:generic_foreign_key_editor', args=[self.item1.pk, 'objectclass'])
        response = self.client.get(check_url)
        self.assertEqual(response.status_code,302)  # user must login too see

        response = self.client.post(check_url,{'objectClass':''})
        self.assertEqual(response.status_code,302)
        self.item1 = self.item1.__class__.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1.objectClass is not None)

        self.login_editor()
        response = self.client.get(check_url)
        self.assertEqual(response.status_code,200)

        response = self.client.post(check_url,{'objectClass':''})
        self.assertEqual(response.status_code,302)
        self.item1 = self.item1.__class__.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1.objectClass is None)

        response = self.client.post(check_url,{'objectClass':self.prop.pk})
        self.assertEqual(response.status_code,200)
        self.item1 = self.item1.__class__.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1.objectClass is None)

        another_oc = models.ObjectClass.objects.create(
            name="editor can't see this",
            definition="my definition",
        )
        response = self.client.post(check_url,{'objectClass':another_oc.pk})
        self.assertEqual(response.status_code,200)
        self.item1 = self.item1.__class__.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1.objectClass is None)


        response = self.client.post(check_url,{'objectClass':self.oc.pk})
        self.assertEqual(response.status_code,302)
        self.item1 = self.item1.__class__.objects.get(pk=self.item1.pk)
        self.assertTrue(self.item1.objectClass == self.oc)

    def test_regular_cannot_save_a_property_they_cant_see_via_edit_page(self):
        self.login_regular_user()
        self.regular_item = self.itemType.objects.create(name="regular item",definition="my definition", submitter=self.regular,**self.defaults)
        response = self.client.get(reverse('aristotle:edit_item',args=[self.regular_item.id]))
        self.assertEqual(response.status_code,200)

        updated_item = utils.model_to_dict_with_change_time(response.context['item'])
        updated_name = updated_item['name'] + " updated!"
        updated_item['name'] = updated_name

        different_prop = models.Property.objects.create(
            name="sub item prop 2",
            workgroup=self.item1.workgroup
        )
        updated_item['property'] = different_prop.pk

        self.assertFalse(self.prop.can_view(self.regular))
        self.assertFalse(different_prop.can_view(self.regular))

        response = self.client.post(reverse('aristotle:edit_item',args=[self.regular_item.id]), updated_item)
        self.regular_item = self.itemType.objects.get(pk=self.regular_item.pk)

        self.assertEqual(response.status_code,200)
        self.assertTrue('not one of the available choices' in response.context['form'].errors['property'][0])
        self.assertFalse(self.regular_item.name == updated_name)
        self.assertFalse(self.regular_item.property == self.prop)

    def test_cascade_action(self):
        self.logout()
        check_url = reverse('aristotle:check_cascaded_states', args=[self.item1.pk])

        response = self.client.get(check_url)
        self.assertEqual(response.status_code,403)

        self.login_editor()

        response = self.client.get(check_url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response, self.item1.objectClass.name)
        self.assertContains(response, self.item1.property.name)

        ra = models.RegistrationAuthority.objects.create(name="new RA")
        item = self.item1.property
        s = models.Status.objects.create(
                concept=item,
                registrationAuthority=ra,
                registrationDate=timezone.now(),
                state=ra.locked_state
                )
        s = models.Status.objects.create(
                concept=item,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=ra.locked_state
                )
        s = models.Status.objects.create(
                concept=self.item1,
                registrationAuthority=self.ra,
                registrationDate=timezone.now(),
                state=ra.public_state
                )

        response = self.client.get(check_url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response, self.item1.objectClass.name)
        self.assertContains(response, self.item1.property.name)
        self.assertContains(response, 'fa-times') # The property has a different status

    def test_user_can_not_see_sub_components_without_permission(self):
        self.prop.workgroup = self.wg2
        self.prop.save()
        self.assertTrue(perms.user_can_view(self.viewer, self.item1))
        self.assertFalse(perms.user_can_view(self.viewer, self.prop))

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item',
            reverse_args=[self.item1.id, 'dataelementconcept', 'name'],
            status_code=200
        )
        self.assertNotContains(response, self.prop.name)


class DataElementViewPage(LoggedInViewConceptPages, TestCase):
    url_name='dataElement'
    itemType=models.DataElement

    def add_dec(self, wg):
        dec = models.DataElementConcept.objects.create(
            name='test dec',
            definition='just a test',
            workgroup=wg
        )
        self.item1.dataElementConcept = dec
        self.item1.save()

    def test_cascade_action(self):
        self.logout()
        check_url = reverse('aristotle:check_cascaded_states', args=[self.item1.pk])
        self.dec1 = models.DataElementConcept.objects.create(name='DEC1 - visible',definition="my definition",workgroup=self.wg1)
        self.item1.dataElementConcept = self.dec1
        self.item1.save()

        response = self.client.get(check_url)
        self.assertEqual(response.status_code,403)

        self.login_editor()

        response = self.client.get(check_url)
        self.assertEqual(response.status_code,200)

    @tag('version')
    def test_version_display_components(self):

        self.add_dec(self.wg1)
        self.update_defn_with_versions()

        latest = reversion.models.Version.objects.get_for_object(self.item1).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        item_context = response.context['item']
        components = item_context['item_data']['Components']

        dec_ht = models.DataElement._meta.get_field('dataElementConcept').help_text

        self.assertTrue(components['Data Element Concept'].is_link)
        self.assertEqual(components['Data Element Concept'].obj, self.item1.dataElementConcept._concept_ptr)
        self.assertEqual(components['Data Element Concept'].link_id, self.item1.dataElementConcept.id)
        self.assertEqual(components['Data Element Concept'].help_text, dec_ht)

    @tag('version')
    def test_version_display_component_from_multi_revision(self):

        dec1 = models.DataElementConcept.objects.create(
            name='dec1',
            definition='just a test',
            workgroup=self.wg1
        )

        dec2 = models.DataElementConcept.objects.create(
            name='dec2',
            definition='just a test',
            workgroup=self.wg1
        )

        self.item1.dataElementConcept = dec1
        self.item2.dataElementConcept = dec2

        with reversion.create_revision():
            self.item1.save()
            self.item2.save()

        latest = reversion.models.Version.objects.get_for_object(self.item1).first()

        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        components = response.context['item']['item_data']['Components']
        self.assertEqual(components['Data Element Concept'].obj, self.item1.dataElementConcept._concept_ptr)

    @tag('version')
    def test_version_display_component_permission(self):
        self.add_dec(None)
        self.update_defn_with_versions()

        latest = reversion.models.Version.objects.get_for_object(self.item1).first()
        self.login_viewer()
        response = self.reverse_get(
            'aristotle:item_version',
            reverse_args=[latest.id],
            status_code=200
        )

        components = response.context['item']['item_data']['Components']

        self.assertFalse(components['Data Element Concept'].is_link, False)
        self.assertTrue(components['Data Element Concept'].value.startswith('Linked to object'))

class DataElementDerivationViewPage(LoggedInViewConceptPages, TestCase):
    url_name='dataelementderivation'
    itemType=models.DataElementDerivation

    def create_linked_ded(self):

        self.de1 = models.DataElement.objects.create(name='DE1 Name',definition="my definition",workgroup=self.wg1)
        self.de2 = models.DataElement.objects.create(name='DE2 Name',definition="my definition",workgroup=self.wg1)
        self.de3 = models.DataElement.objects.create(name='DE3 Name',definition="my definition",workgroup=self.wg1)
        self.ded = models.DataElementDerivation.objects.create(name='DED Name', definition='my definition', workgroup=self.wg1)

        ded_derives_1 = models.DedDerivesThrough.objects.create(data_element_derivation=self.ded, data_element=self.de1, order=0)
        ded_derives_2 = models.DedDerivesThrough.objects.create(data_element_derivation=self.ded, data_element=self.de2, order=1)
        ded_derives_3 = models.DedDerivesThrough.objects.create(data_element_derivation=self.ded, data_element=self.de3, order=2)

        ded_inputs_1 = models.DedInputsThrough.objects.create(data_element_derivation=self.ded, data_element=self.de3, order=0)
        ded_inputs_1 = models.DedInputsThrough.objects.create(data_element_derivation=self.ded, data_element=self.de2, order=1)
        ded_inputs_1 = models.DedInputsThrough.objects.create(data_element_derivation=self.ded, data_element=self.de1, order=2)

        return self.ded

    def derivation_m2m_concepts_save(self, url, attr):
        self.de1 = models.DataElement.objects.create(name='DE1 - visible',definition="my definition",workgroup=self.wg1)
        self.de2 = models.DataElement.objects.create(name='DE2 - not visible',definition="my definition",workgroup=self.wg2)
        self.oc1 = models.ObjectClass.objects.create(name='OC - visible but wrong',definition="my definition",workgroup=self.wg1)

        self.login_editor()

        management_form = {
            'form-INITIAL_FORMS': 0,
            'form-TOTAL_FORMS': 1,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000
        }

        self.assertFalse(self.de2.can_view(self.editor))

        response = self.client.get(
            reverse(url, args=[self.item1.pk])
        )
        self.assertEqual(response.status_code,200)

        postdata = management_form.copy()
        postdata['form-0-item_to_add'] = self.de2.pk
        postdata['form-0-ORDER'] = 0
        #postdata['form-TOTAL_FORMS'] = 2

        response = self.client.post(
            reverse(url, args=[self.item1.pk]),
            postdata
        )
        self.item1 = self.itemType.objects.get(pk=self.item1.pk)
        self.assertTrue(self.de2 not in getattr(self.item1, attr).all())
        self.assertEqual(response.status_code,200)
        self.assertContains(response, 'Select a valid choice')

        postdata = management_form.copy()
        postdata['form-0-item_to_add'] = self.de1.pk
        postdata['form-0-ORDER'] = 0
        postdata['form-1-item_to_add'] = self.de2.pk
        postdata['form-1-ORDER'] = 1
        postdata['form-TOTAL_FORMS'] = 2

        response = self.client.post(
            reverse(url, args=[self.item1.pk]),
            postdata,
            follow=True
        )
        self.assertTrue(self.de2 not in getattr(self.item1, attr).all())
        self.assertContains(response, 'Select a valid choice')
        self.assertEqual(response.status_code,200)

        # user can see OC1, but its the wrong type so expect failure

        postdata = management_form.copy()
        postdata['form-0-item_to_add'] = self.de1.pk
        postdata['form-0-ORDER'] = 0
        postdata['form-1-item_to_add'] = self.oc1.pk
        postdata['form-1-ORDER'] = 1
        postdata['form-TOTAL_FORMS'] = 2

        response = self.client.post(
            reverse(url, args=[self.item1.pk]),
            postdata,
            follow=True
        )
        self.assertTrue(self.de2 not in getattr(self.item1, attr).all())
        self.assertContains(response, 'Select a valid choice')
        self.assertEqual(response.status_code,200)

        postdata = management_form.copy()
        postdata['form-0-item_to_add'] = self.de1.pk
        postdata['form-0-ORDER'] = 0

        response = self.client.post(
            reverse(url, args=[self.item1.pk]),
            postdata
        )
        self.assertTrue(self.de1 in getattr(self.item1, attr).all())
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response, self.item1.get_absolute_url())

    def test_derivation_derives_concepts_save(self):
        self.derivation_m2m_concepts_save(
            url="aristotle_mdr:dataelementderivation_change_derives",
            attr='derives',
        )

    def test_derivation_inputs_concepts_save(self):
        self.derivation_m2m_concepts_save(
            url="aristotle_mdr:dataelementderivation_change_inputs",
            attr='inputs',
        )

    def derivation_m2m_formset(self, url, attr, prefix='form', item_add_field='item_to_add', add_itemdata=False, extra_postdata=None):

        self.de1 = models.DataElement.objects.create(name='DE1 - visible',definition="my definition",workgroup=self.wg1)
        self.de2 = models.DataElement.objects.create(name='DE2 - visible',definition="my definition",workgroup=self.wg1)
        self.de3 = models.DataElement.objects.create(name='DE3 - visible',definition="my definition",workgroup=self.wg1)

        self.login_editor()

        management_form = {
            '{}-INITIAL_FORMS'.format(prefix): 0,
            '{}-TOTAL_FORMS'.format(prefix): 1,
            '{}-MIN_NUM_FORMS'.format(prefix): 0,
            '{}-MAX_NUM_FORMS'.format(prefix): 1000
        }

        if extra_postdata:
            management_form.update(extra_postdata)

        # Post 3 items
        postdata = management_form.copy()

        if add_itemdata:
            postdata.update(utils.model_to_dict_with_change_time(self.item1))

        postdata['{}-0-{}'.format(prefix, item_add_field)] = self.de3.pk
        postdata['{}-0-ORDER'.format(prefix)] = 0
        postdata['{}-1-{}'.format(prefix, item_add_field)] = self.de1.pk
        postdata['{}-1-ORDER'.format(prefix)] = 1
        postdata['{}-2-{}'.format(prefix, item_add_field)] = self.de2.pk
        postdata['{}-2-ORDER'.format(prefix)] = 2
        postdata['{}-TOTAL_FORMS'.format(prefix)] = 3

        response = self.client.post(
            reverse(url, args=[self.item1.pk]),
            postdata
        )

        self.assertRedirects(response, self.item1.get_absolute_url())

        items = getattr(self.item1, attr).all()
        self.assertTrue(self.de1 in items)
        self.assertTrue(self.de2 in items)
        self.assertTrue(self.de3 in items)

        # Load page to check loading of existing data and preserved order

        response = self.client.get(reverse(url, args=[self.item1.pk]))
        self.assertEqual(response.status_code, 200)

        if not add_itemdata:
            # If m2m specific form
            formset_initial = response.context['formset'].initial

            self.assertEqual(len(formset_initial), 3)
            for data in formset_initial:
                self.assertTrue(data['ORDER'] in [0,1,2])
                if data['ORDER'] == 0:
                    self.assertEqual(data['{}'.format(item_add_field)], self.de3)
                elif data['ORDER'] == 1:
                    self.assertEqual(data['{}'.format(item_add_field)], self.de1)
                elif data['ORDER'] == 2:
                    self.assertEqual(data['{}'.format(item_add_field)], self.de2)

        if attr == 'derives':
            through_model = models.DedDerivesThrough
        else:
            through_model = models.DedInputsThrough

        # Check order with through table
        self.assertEqual(through_model.objects.count(), 3)
        self.assertEqual(through_model.objects.get(order=0).data_element, self.de3)
        self.assertEqual(through_model.objects.get(order=1).data_element, self.de1)
        self.assertEqual(through_model.objects.get(order=2).data_element, self.de2)


        # Change order and delete
        postdata = management_form.copy()

        if add_itemdata:
            postdata.update(utils.model_to_dict_with_change_time(self.item1))

        postdata['{}-0-{}'.format(prefix, item_add_field)] = self.de3.pk
        postdata['{}-0-id'.format(prefix)] = through_model.objects.get(data_element=self.de3).pk
        postdata['{}-0-ORDER'.format(prefix)] = 0
        postdata['{}-0-DELETE'.format(prefix)] = 'checked'
        postdata['{}-1-{}'.format(prefix, item_add_field)] = self.de2.pk
        postdata['{}-1-id'.format(prefix)] = through_model.objects.get(data_element=self.de2).pk
        postdata['{}-1-ORDER'.format(prefix)] = 1
        postdata['{}-2-{}'.format(prefix, item_add_field)] = self.de1.pk
        postdata['{}-2-id'.format(prefix)] = through_model.objects.get(data_element=self.de1).pk
        postdata['{}-2-ORDER'.format(prefix)] = 2
        postdata['{}-TOTAL_FORMS'.format(prefix)] = 3
        postdata['{}-INITIAL_FORMS'.format(prefix)] = 3

        response = self.client.post(
            reverse(url, args=[self.item1.pk]),
            postdata
        )
        print(response.status_code)

        self.assertRedirects(response, self.item1.get_absolute_url())

        items = getattr(self.item1, attr).all()
        self.assertTrue(items.count(), 2)
        self.assertTrue(self.de1 in items)
        self.assertTrue(self.de2 in items)
        self.assertFalse(self.de3 in items)

        # Load page to check order

        response = self.client.get(reverse(url, args=[self.item1.pk]))
        self.assertEqual(response.status_code, 200)

        formset_initial = response.context['formset'].initial

        if not add_itemdata:
            # If m2m specific form
            self.assertEqual(len(formset_initial), 2)
            for data in formset_initial:
                self.assertTrue(data['ORDER'] in [1,2])
                if data['ORDER'] == 1:
                    self.assertEqual(data['{}'.format(item_add_field)], self.de2)
                elif data['ORDER'] == 2:
                    self.assertEqual(data['{}'.format(item_add_field)], self.de1)

        # Check order with through table
        self.assertEqual(through_model.objects.count(), 2)
        self.assertEqual(through_model.objects.get(order=1).data_element, self.de2)
        self.assertEqual(through_model.objects.get(order=2).data_element, self.de1)

    @tag('edit_formsets')
    def test_derivation_inputs_formset(self):
        self.derivation_m2m_formset(
            url="aristotle_mdr:dataelementderivation_change_inputs",
            attr='inputs',
        )

    @tag('edit_formsets')
    def test_derivation_derives_formset(self):
        self.derivation_m2m_formset(
            url="aristotle_mdr:dataelementderivation_change_derives",
            attr='derives',
        )

    @tag('edit_formsets')
    def test_derivation_inputs_formset_editor(self):

        self.derivation_m2m_formset(
            url="aristotle_mdr:edit_item",
            attr="inputs",
            prefix="inputs",
            item_add_field="data_element",
            add_itemdata=True,
        )

    @tag('edit_formsets')
    def test_derivation_derives_formset_editor(self):

        self.derivation_m2m_formset(
            url="aristotle_mdr:edit_item",
            attr="derives",
            prefix="derives",
            item_add_field="data_element",
            add_itemdata=True,
        )

    def test_derivation_item_page(self):

        ded = self.create_linked_ded()

        self.login_editor()
        response = self.client.get(reverse("aristotle:item", args=[ded.pk]), follow=True)

        self.assertEqual(response.status_code, 200)

        # Check the template tag that was used returned the correct data

        item = response.context['item']

        des = get_dataelements_from_m2m(item, "inputs")
        self.assertEqual(des[0].pk, self.de3.pk)
        self.assertEqual(des[1].pk, self.de2.pk)
        self.assertEqual(des[2].pk, self.de1.pk)

        des = get_dataelements_from_m2m(item, "derives")
        self.assertEqual(des[0].pk, self.de1.pk)
        self.assertEqual(des[1].pk, self.de2.pk)
        self.assertEqual(des[2].pk, self.de3.pk)

    @skip('to be fixed in future')
    @tag('ded_version')
    def test_derivation_version_follow(self):

        ded = self.create_linked_ded()

        with reversion.create_revision():
            ded.save()

        versions = reversion.models.Version.objects.get_for_object(ded)
        self.assertEqual(versions.count(), 1)

        version = versions.first()

        data = json.loads(version.serialized_data)
        self.assertEqual(len(data), 1)

        self.assertTrue('derivation_rule' in data[0]['fields'])
        self.assertTrue('derives' in data[0]['fields'])
        self.assertTrue('inputs' in data[0]['fields'])


class LoggedInViewUnmanagedPages(utils.LoggedInViewPages):
    defaults = {}
    def setUp(self):
        super().setUp()
        self.item1 = self.itemType.objects.create(name="OC1",**self.defaults)

    def get_page(self,item):
        url_name = "".join(item._meta.verbose_name.title().split())
        url_name = url_name[0].lower() + url_name[1:]
        return reverse('aristotle:%s'%url_name,args=[item.id])

    def test_help_page_exists(self):
        self.logout()
        #response = self.client.get(self.get_help_page())
        #self.assertEqual(response.status_code,200)

    def test_item_page_exists(self):
        self.logout()
        response = self.client.get(self.get_page(self.item1))
        self.assertEqual(response.status_code,200)

class MeasureViewPage(LoggedInViewUnmanagedPages, TestCase):
    url_name='measure'
    itemType=models.Measure

    def setUp(self):
        super().setUp()

        self.item2 = models.UnitOfMeasure.objects.create(name="OC1",workgroup=self.wg1,measure=self.item1,**self.defaults)

class RegistrationAuthorityViewPage(LoggedInViewUnmanagedPages, TestCase):
    url_name='registrationAuthority'
    itemType=models.RegistrationAuthority

    def setUp(self):
        super().setUp()

        self.item2 = models.DataElement.objects.create(name="OC1",workgroup=self.wg1,**self.defaults)

        models.Status.objects.create(
            concept=self.item2,
            registrationAuthority=self.item1,
            registrationDate=timezone.now(),
            state=models.STATES.standard
        )

    def get_page(self,item):
        return item.get_absolute_url()

    def test_view_all_ras(self):
        self.logout()
        response = self.client.get(reverse('aristotle:all_registration_authorities'))
        self.assertEqual(response.status_code,200)

class OrganizationViewPage(LoggedInViewUnmanagedPages, TestCase):
    url_name='organization'
    itemType=models.Organization

    def setUp(self):
        super().setUp()

    def get_page(self,item):
        return item.get_absolute_url()

    def test_view_all_orgs(self):
        self.logout()
        response = self.client.get(reverse('aristotle:all_organizations'))
        self.assertEqual(response.status_code,200)
