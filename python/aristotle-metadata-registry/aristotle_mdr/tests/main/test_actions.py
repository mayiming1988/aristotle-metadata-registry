# Unit tests for action that don't fit in test_html_pages
from django.test import TestCase

from aristotle_mdr import models
from aristotle_mdr.views.editors import CloneItemView


class CloneViewTestCase(TestCase):

    def setUp(self):
        self.view = CloneItemView()
        vd = models.ValueDomain.objects.create(
            name='Goodness',
            definition='A measure of good'
        )
        models.PermissibleValue.objects.create(
            value='1',
            meaning='Not very good',
            valueDomain=vd,
            order=0
        )
        models.PermissibleValue.objects.create(
            value='10',
            meaning='Very good',
            valueDomain=vd,
            order=1
        )
        self.view.item = vd
        self.view.model = type(vd)

    def test_component_cloning(self):
        clone = models.ValueDomain.objects.create(
            name='Goodness clone',
            definition='A measure of good'
        )
        self.view.clone_components(clone)
        self.assertEqual(clone.permissiblevalue_set.count(), 2)
        self.assertEqual(clone.permissiblevalue_set.get(order=0).meaning, 'Not very good')
        self.assertEqual(clone.permissiblevalue_set.get(order=1).meaning, 'Very good')
