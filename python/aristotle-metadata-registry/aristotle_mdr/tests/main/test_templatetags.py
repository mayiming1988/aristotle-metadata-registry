from django.template import Context, Template
from django.test import TestCase, override_settings
from django.utils.safestring import SafeString
from django.core.exceptions import FieldDoesNotExist
from django.template.exceptions import TemplateSyntaxError

import aristotle_mdr.models as models
from aristotle_mdr.templatetags import util_tags

from datetime import datetime, date


preamble = "{% load aristotle_tags %}"


class TestTemplateTags_aristotle_tags_py(TestCase):
    def setUp(self):
        self.steward_org_1 = models.StewardOrganisation.objects.create(name="Test SO")
        self.ra = models.RegistrationAuthority.objects.create(name="Test RA", stewardship_organisation=self.steward_org_1)
        self.wg = models.Workgroup.objects.create(name="Test WG 1", stewardship_organisation=self.steward_org_1)
        self.wg.registrationAuthorities=[self.ra]
        self.wg.save()
        self.item = models.ObjectClass.objects.create(name="Test OC1", workgroup=self.wg)

    def test_doc(self):
        context = Context({"item": self.item})

        # Definition has helptext
        template = Template(preamble + "{% doc item 'definition' %}")
        template = template.render(context)
        self.assertTrue('Representation of a concept by a descriptive statement' in template)

        # Modified does not (it comes from django-model-utils
        template = Template(preamble + "{% doc item 'modified' %}")
        template = template.render(context)
        self.assertTrue('No help text for the field' in template)

        template = Template(preamble + "{% doc item %}")
        template.render(context)

        with self.assertRaises(FieldDoesNotExist):
            template = Template(preamble + "{% doc item 'not_an_attribute' %}")
            template.render(context)

    def use_safe_filter(self, safefilter):
        context = Context({"item": self.item})

        template = Template(preamble + "{{ 'comment'|%s:'user' }}" % (safefilter))
        page = template.render(context).replace('\n', '').strip()
        self.assertEqual(page, 'False')

        with self.assertRaises(TemplateSyntaxError):
            template = Template(preamble + "{{ 'comment'|%s }}" % (safefilter))
            template.render(context)

    def test_can_alter_comment(self):
        self.use_safe_filter('can_alter_comment')

    def test_can_alter_post(self):
        self.use_safe_filter('can_alter_post')

    def test_in_workgroup(self):
        self.use_safe_filter('in_workgroup')


class UtilTagsTestCase(TestCase):

    def test_blech_strings_safe(self):
        """Make sure strings returned by bleach are marked safe"""
        html = '<b>Bold</b> <u>Underline</u>'
        bleached = util_tags.bleach_filter(html)
        self.assertEqual(type(bleached), SafeString)

    @override_settings(BLEACH_ALLOWED_TAGS=['a'])
    def test_bleach_non_allowed_tags(self):
        html = '<b>Bold</b> <u>Underline</u>'
        bleached = util_tags.bleach_filter(html)
        self.assertEqual(bleached, 'Bold Underline')

    @override_settings(BLEACH_ALLOWED_TAGS=['a'])
    def test_bleach_mixed_tags(self):
        html = '<a>Link</a> <u>Underline</u>'
        bleached = util_tags.bleach_filter(html)
        self.assertEqual(bleached, '<a>Link</a> Underline')

    @override_settings(BLEACH_ALLOWED_TAGS=['a'])
    @override_settings(BLEACH_ALLOWED_ATTRIBUTES={'a': 'href'})
    def test_bleach_removes_not_allowed_attrs(self):
        html = '<a href="/url" title="Wow">Link</a>'
        bleached = util_tags.bleach_filter(html)
        self.assertEqual(bleached, '<a href="/url">Link</a>')

    def test_bleach_tag_case(self):
        """Test that bleach handles tags being uppercase"""
        html = '<B>Bold</B>'
        bleached = util_tags.bleach_filter(html)
        self.assertEqual(bleached, '<b>Bold</b>')

    def test_bleach_handles_none(self):
        bleached = util_tags.bleach_filter(None)
        self.assertIsNone(bleached)

    def test_iso_time_datetime(self):
        dt = datetime(2000, 10, 10, 1, 1, 1)
        isotime = util_tags.iso_time(dt)
        self.assertEqual(isotime, '2000-10-10T01:01:01')

    def test_iso_time_date(self):
        dt = date(2000, 10, 10)
        isotime = util_tags.iso_time(dt)
        self.assertEqual(isotime, '2000-10-10')

    def test_iso_time_none(self):
        dt = None
        isotime = util_tags.iso_time(dt)
        self.assertEqual(isotime, '-')

    def test_iso_time_bad_type(self):
        dt = 55
        isotime = util_tags.iso_time(dt)
        self.assertEqual(isotime, 55)
