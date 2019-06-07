from django.test import TestCase

from aristotle_mdr.tests.utils import AristotleTestUtils
import aristotle_mdr.models as MDR
from aristotle_dse.models import DataSetSpecification

import json
import reversion


class SerializerTestCase(AristotleTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        self.object_class = MDR.ObjectClass.objects.create(
            name='Person',
            definition='A human being',
            submitter=self.editor
        )

        # TODO: add other fields
        self.data_set_specification = DataSetSpecification.objects.create(
            name='Person DSS',
            definition='A data set specification about people',
            submitter=self.editor
        )

    def create_version(self):
        with reversion.create_revision():
            self.object_class.definition = 'No longer a human being'
            self.object_class.name = 'New Person'
            self.object_class.save()

    def get_serialized_data_dict(self, concept):
        version = reversion.models.Version.objects.get_for_object(self.object_class).first()
        return json.loads(version.serialized_data)


    def get_app_label(self, concept):
        return concept._meta.label_lower

    def test_basic_fields_serialized(self):
        """ Test that the basic concrete model fields were serialized """
        self.create_version()

        serialized_data = self.get_serialized_data_dict(self.object_class)

        # Confirm presence of basic fields in serialized data
        self.assertEqual(serialized_data['name'], 'New Person')
        self.assertEqual(serialized_data['definition'], 'No longer a human being')

    def test_model_class_serialized(self):
        """ Test that the model class was serialized"""
        self.create_version()

        serialized_data = self.get_serialized_data_dict(self.object_class)

        self.assertEqual(serialized_data['serialized_model'], self.get_app_label(self.object_class))

    def test_custom_fields_serialized(self):
        pass

    def test_slots_serialized(self):
        pass
