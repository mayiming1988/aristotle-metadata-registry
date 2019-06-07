""" Don't run with default aristotle_mdr test settings """

from django.test import TestCase

from aristotle_dse.models import DataSetSpecification
from aristotle_mdr.tests.utils import AristotleTestUtils, model_to_dict_with_change_time
from aristotle_mdr.contrib.custom_fields.models import CustomValue, CustomField
from aristotle_mdr.contrib.custom_fields.types import type_choices as TYPE_CHOICES
import aristotle_mdr.models as MDR

import reversion
import json


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

        self.custom_field = CustomField.objects.create(
            order=1,
            name='A Custom Field',
            type=TYPE_CHOICES.str
        )

        self.custom_value = CustomValue.objects.create(
            field=self.custom_field,
            concept=self.object_class,
            content="Custom values"
        )

    def create_version(self):
        with reversion.create_revision():
            self.object_class.definition = 'No longer a human being'
            self.object_class.name = 'New Person'
            self.object_class.save()

    def get_serialized_data_dict(self, concept):
        version = reversion.models.Version.objects.get_for_object(concept).first()
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
        """ Test that the custom fields were serialized. This does not confirm that editor functionality
         is working correctly, merely that the serialization of custom fields is working"""
        with reversion.create_revision():
            self.object_class.name = 'New Person'
            self.custom_value.content = 'New content'
            self.custom_value.save()
            self.object_class.save()

        serialized_data = self.get_serialized_data_dict(self.object_class)

        self.assertEqual(serialized_data['customvalue_set'][0]['content'], 'New content')

    def test_custom_fields_serialized_from_concept_editor(self):
        """ Test that the custom fields were serialized from the editor"""
        object_class = MDR.ObjectClass.objects.create(
            name='Person',
            definition='A human being',
            submitter=self.editor
        )

        custom_field = CustomField.objects.create(
            name='MyCustomField',
            type='int',
            help_text='Custom',
            order=0
        )

        postdata = model_to_dict_with_change_time(object_class)
        postdata[custom_field.form_field_name] = 4

        self.login_editor()
        self.reverse_post(
            'aristotle:edit_item',
            postdata,
            reverse_args=[object_class.id],
            status_code=302
        )
        serialized_data = self.get_serialized_data_dict(object_class)

        self.assertEqual(int(serialized_data['customvalue_set'][0]['content']), 4)

