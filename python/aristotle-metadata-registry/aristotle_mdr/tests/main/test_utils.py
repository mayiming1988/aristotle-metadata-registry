from django.test import TestCase, tag

from aristotle_mdr import models
from aristotle_mdr.utils import setup_aristotle_test_environment
from aristotle_mdr import utils
from aristotle_mdr.views.versions import VersionField

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

import datetime

setup_aristotle_test_environment()


class UtilsTests(TestCase):

    def setUp(self):

        self.oc1 = models.ObjectClass.objects.create(
            name='Test OC',
            definition='Test Definition'
        )
        self.oc2 = models.ObjectClass.objects.create(
            name='Test OC2',
            definition='Test Definition2'
        )

    def test_reverse_slugs(self):
        item = models.ObjectClass.objects.create(name=" ",definition="my definition",submitter=None)
        ra = models.RegistrationAuthority.objects.create(name=" ",definition="my definition")
        org = models.Organization.objects.create(name=" ",definition="my definition")
        wg = models.Workgroup.objects.create(name=" ",definition="my definition")

        self.assertTrue('--' in utils.url_slugify_concept(item))
        self.assertTrue('--' in utils.url_slugify_workgroup(wg))
        self.assertTrue('--' in utils.url_slugify_registration_authoritity(ra))
        self.assertTrue('--' in utils.url_slugify_organization(org))

    def test_get_aristotle_url(self):

        user = get_user_model().objects.create(
            email='user@example.com',
            password='verysecure'
        )

        item = models.ObjectClass.objects.create(name="tname",definition="my definition",submitter=None)
        ra = models.RegistrationAuthority.objects.create(name="tname",definition="my definition")
        org = models.Organization.objects.create(name="tname",definition="my definition")
        wg = models.Workgroup.objects.create(name="tname",definition="my definition")
        rr = models.ReviewRequest.objects.create(
            requester=user,
            registration_authority=ra,
            state=ra.public_state,
            registration_date=datetime.date(2010,1,1)
        )

        url = utils.get_aristotle_url(item._meta.label_lower, item.pk, item.name)
        self.assertEqual(url, reverse('aristotle:item', args=[item.pk]))

        url = utils.get_aristotle_url(ra._meta.label_lower, ra.pk, ra.name)
        self.assertEqual(url, reverse('aristotle:registrationAuthority', args=[ra.pk, ra.name]))

        url = utils.get_aristotle_url(org._meta.label_lower, org.pk, org.name)
        self.assertEqual(url, reverse('aristotle:organization', args=[org.pk, org.name]))

        url = utils.get_aristotle_url(wg._meta.label_lower, wg.pk, wg.name)
        self.assertEqual(url, reverse('aristotle:workgroup', args=[wg.pk, wg.name]))

        url = utils.get_aristotle_url(rr._meta.label_lower, rr.pk)
        self.assertEqual(url, reverse('aristotle:userReviewDetails', args=[rr.pk]))

        url = utils.get_aristotle_url('aristotle_mdr.fake_model', 7, 'fake_name')
        self.assertTrue(url is None)

    def test_pretify_camel_case(self):
        pcc = utils.utils.pretify_camel_case
        self.assertEqual(pcc('ScopedIdentifier'), 'Scoped Identifier')
        self.assertEqual(pcc('Namespace'), 'Namespace')
        self.assertEqual(pcc('LongerCamelCase'), 'Longer Camel Case')

    @tag('version')
    def test_version_field_value_only(self):

        field = VersionField(
            value='My Value',
            help_text='Help Me'
        )

        self.assertFalse(field.is_link)
        self.assertFalse(field.is_reference)
        self.assertFalse(field.is_list)
        self.assertFalse(field.is_html)
        self.assertEqual(str(field), 'My Value')

    @tag('version')
    def test_version_field_reference(self):

        field = VersionField(
            obj=[self.oc1.id, self.oc2.id],
            reference_label='aristotle_mdr._concept',
            help_text='Help Me'
        )

        self.assertTrue(field.is_reference)
        self.assertTrue(field.is_list)
        self.assertFalse(field.is_link)

        lookup = {
            'aristotle_mdr._concept': {
                self.oc1.id: self.oc1,
                self.oc2.id: self.oc2
            }
        }

        field.dereference(lookup)

        self.assertFalse(field.is_reference)
        self.assertTrue(field.is_link)
        self.assertTrue(field.is_list)

        self.assertCountEqual(field.object_list, [self.oc1, self.oc2])

    @tag('version')
    def test_version_field_list_handling(self):

        field = VersionField(
            obj=[self.oc1],
        )

        self.assertEqual(field.obj, self.oc1)
        self.assertFalse(field.is_list)

        field = VersionField(
            obj=[],
        )

        self.assertFalse(field.is_link)
        self.assertTrue(field.is_list)

        field = VersionField(
            value=[]
        )

        self.assertFalse(field.is_link)
        self.assertFalse(field.is_list)
        self.assertEqual(str(field), 'None')

    @tag('version')
    def test_version_field_obj_display(self):

        field = VersionField(
            obj=self.oc1,
        )

        self.assertTrue(field.is_link)
        self.assertFalse(field.is_list)
        self.assertFalse(field.is_reference)
        self.assertEqual(str(field), self.oc1.name)
        self.assertEqual(field.link_id, self.oc1.id)

    @tag('version')
    def test_version_field_component_display(self):

        vd = models.ValueDomain.objects.create(
            name='Test Value Domain',
            definition='Test Definition'
        )
        pv = models.PermissibleValue.objects.create(
            value='Val',
            meaning='Mean',
            valueDomain=vd,
            order=0
        )

        field = VersionField(
            obj=pv
        )

        self.assertTrue(field.is_link)
        self.assertFalse(field.is_list)
        self.assertFalse(field.is_reference)
        self.assertEqual(str(field), str(pv))
        self.assertEqual(field.link_id, vd.id)

    @tag('version')
    def test_version_field_invalid_lookup(self):

        field = VersionField(
            obj=[2],
            reference_label='aristotle_mdr._concept'
        )

        self.assertFalse(field.is_link)
        self.assertTrue(field.is_reference)

        field.dereference({})

        self.assertFalse(field.is_link)
        self.assertFalse(field.is_reference)
        self.assertEqual(str(field), field.perm_message)
