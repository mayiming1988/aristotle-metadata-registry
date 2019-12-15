# Unit tests for action that don't fit in test_html_pages
from django.test import TestCase, tag

from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr.views.editors import CloneItemView
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

