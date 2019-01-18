from django.test import TestCase, tag, override_settings
from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr import models as mdr_models


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

    @override_settings(ARISTOTLE_SETTINGS={
        'CONTENT_EXTENSIONS': ['aristotle_mdr_backwards']
    })
    def test_field_avaliable_when_backwards_enabled(self):
        form = self.get_vd_edit_form()
        self.assertTrue('classification_scheme' in form.fields)

    def test_field_hidden_when_backwards_not_enabled(self):
        form = self.get_vd_edit_form()
        self.assertFalse('classification_scheme' in form.fields)
