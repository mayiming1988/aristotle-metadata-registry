from django.test import TestCase, tag

from aristotle_mdr import models


class ModelsTestCase(TestCase):
    """Testing for properties and methods on models"""

    def setUp(self):
        self.oc = models.ObjectClass.objects.create(
            name='Fish',
            definition='Them sea creatures'
        )
        self.concept = self.oc._concept_ptr

    def decache(self, item):
        item._type = None
        item.save()

    def test_dot_item(self):
        item = self.concept.item
        self.assertEqual(item, self.oc)

    def test_dot_item_no_cache(self):
        self.decache(self.concept)
        self.test_dot_item()
        # item = self.concept.item
        # self.assertEqual(item, self.oc)

    def test_item_type(self):
        ct = self.concept.item_type
        self.assertEqual(ct.model_class(), models.ObjectClass)

    def test_item_type_no_cache(self):
        self.decache(self.concept)
        self.test_item_type()

    def test_item_type_name(self):
        name = self.concept.item_type_name
        self.assertEqual(name, 'Object Class')

    def test_item_type_name_no_cache(self):
        self.decache(self.concept)
        self.test_item_type_name()
