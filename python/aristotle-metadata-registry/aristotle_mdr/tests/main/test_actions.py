# Unit tests for action that don't fit in test_html_pages
from django.test import TestCase, tag

from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr.views.editors import CloneItemView
from aristotle_mdr import models
from aristotle_mdr import models


@tag('clone')
class CloneViewTestCase(AristotleTestUtils, TestCase):

    def setUp(self):
        super().setUp()
        self.view = CloneItemView()
        self.vd = models.ValueDomain.objects.create(
            name='Goodness',
            definition='A measure of good',
            workgroup=self.wg1
        )
        models.PermissibleValue.objects.create(
            value='1',
            meaning='Not very good',
            valueDomain=self.vd,
            order=0
        )
        models.PermissibleValue.objects.create(
            value='10',
            meaning='Very good',
            valueDomain=self.vd,
            order=1
        )
        self.view.item = self.vd
        self.view.model = type(self.vd)

    @tag('unit')
    def test_clone_components_function(self):
        clone = models.ValueDomain.objects.create(
            name='Goodness clone',
            definition='A measure of good'
        )
        self.view.clone_components(clone)
        self.assertEqual(clone.permissiblevalue_set.count(), 2)
        self.assertEqual(clone.permissiblevalue_set.get(order=0).meaning, 'Not very good')
        self.assertEqual(clone.permissiblevalue_set.get(order=1).meaning, 'Very good')
