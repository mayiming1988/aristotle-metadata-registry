from django.test import TestCase, tag, override_settings
from django.core.cache import cache
from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr.contrib.aristotle_backwards import models
from aristotle_mdr import models as mdr_models
from aristotle_mdr.tests.main.test_html_pages import LoggedInViewConceptPages
from aristotle_mdr.tests.main.test_admin_pages import AdminPageForConcept


@tag('backwards')
class AristotleBackwardsTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.vd = mdr_models.ValueDomain.objects.create(
            name='Hella sick values',
            definition='Hella good',
            workgroup=self.wg1
        )

    def get_vd_edit_form(self):
        self.login_editor()
        response = self.reverse_get(
            'aristotle:edit_item',
            reverse_args=[self.vd.id]
        )
        return response.context['form']

    def test_field_avaliable_when_backwards_enabled(self):
        form = self.get_vd_edit_form()
        self.assertTrue('classification_scheme' in form.fields)

    @override_settings(ARISTOTLE_SETTINGS={
        'CONTENT_EXTENSIONS': [],
        'SEPARATORS': {}
    })
    def test_field_hidden_when_backwards_not_enabled(self):
        form = self.get_vd_edit_form()
        self.assertFalse('classification_scheme' in form.fields)


class ClassificationSchemeViewPage(LoggedInViewConceptPages, TestCase):
    itemType=models.ClassificationScheme

    def setUp(self):
        super().setUp()
        cache.clear()


class ClassificationSchemeAdminPage(AdminPageForConcept, TestCase):
    itemType=models.ClassificationScheme

    def setUp(self):
        super().setUp()
        cache.clear()
