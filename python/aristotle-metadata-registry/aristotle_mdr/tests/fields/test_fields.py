from aristotle_mdr.tests.utils import AristotleTestUtils
from aristotle_mdr.contrib.serializers.utils import get_concept_fields

from django.test import TestCase


class FieldsTestMixin(AristotleTestUtils, TestCase):
    def setUp(self):
        super().setUp()
        concept_fields = get_concept_fields
