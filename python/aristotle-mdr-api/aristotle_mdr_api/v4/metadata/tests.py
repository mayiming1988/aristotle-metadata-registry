from django.urls import reverse
from rest_framework import status
from aristotle_mdr_api.v4.tests import BaseAPITestCase
from aristotle_mdr import models as mdr_models
from aristotle_mdr.contrib.custom_fields.models import CustomField


class MetadataRedirectionAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        self.item = mdr_models.ObjectClass.objects.create(
            name='Test Concept',
            definition='Concept Definition',
            submitter=self.user,
        )

        self.login_user()

    def test_get_metadata_type_redirection_works_and_matches_uuid_and_type(self):

        response = self.client.get(
            reverse('api_v4:metadata:get_metadata_type_from_uuid', kwargs={"item_uuid": self.item.uuid}),
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(str(self.item.uuid) in response.url.split("/"))
        self.assertTrue(self.item.item_type.model in response.url.split("/"))

    def test_api_serialiser_response_status_is_200_and_fields_are_shown(self):

        response = self.client.get(
            reverse(
                'api_v4:metadata:generic_metadata_serialiser_api_endpoint',
                kwargs={
                    "item_uuid": self.item.uuid,
                    "metadata_type": self.item.item_type.model,
                }
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            {"name": self.item.name, "definition": self.item.definition},
            {"name": response.data['name'], "definition": response.data['definition']},
        )


class ListOrCreateMetadataGetRequest(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        self.value_domain_1 = mdr_models.ValueDomain.objects.create(
            name='Test Value Domain 1',
            definition='VD Definition',
            submitter=self.user,
        )

        self.value_domain_2 = mdr_models.ValueDomain.objects.create(
            name='Test Value Domain 2',
            definition='VD Definition',
            submitter=self.user,
        )

        self.custom_field_1 = CustomField.objects.create(
            name="Test CustomField",
            order=1,
        )

        self.custom_field_2 = CustomField.objects.create(
            name="Test CustomField",
            order=2,
        )

        self.login_user()

    def test_api_list_or_create_metadata_get_request(self):

        response = self.client.get(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.ValueDomain.__name__.lower(),
                }
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Make sure response is OK.
        self.assertEqual(len(response.data['results']), 2)  # Make sure the length is correct.
        self.assertEqual(response.data['count'], 2)  # Make sure the length is correct.
        self.assertIsNone(response.data['next'])  # Make sure the paginator works.
        self.assertIsNone(response.data['previous'])  # Make sure the paginator works.

    def test_api_list_or_create_metadata_post_request(self):

        post_data = {
            "name": "Total Australian currency N[N(8)]",
            "definition": "Total number of Australian dollars.",
        }

        response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.ValueDomain.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_list_or_create_metadata_post_request_with_foreign_keys(self):

        post_data = {
            "name": "MY TEST DATA ELEMENT",
            "definition": "DEFINITION FOR MY TEST DATA ELEMENT",
            "origin": "Blah blah...",
            "valueDomain": self.value_domain_1.id,
        }

        response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.DataElement.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertDictEqual(
            {"name": self.value_domain_1.id},
            {"name": response.data['valueDomain']},
        )

    def test_api_list_or_create_metadata_post_request_for_data_element_with_subcomponents(self):

        post_data = {
            "name": "MY DATA ELEMENT WITH CUSTOM VALUES",
            "definition": "THIS DATA ELEMENT HAS CUSTOM VALUES.",
            "workgroup": self.wg.id,
            "customvalue_set": [
                {
                    "content": "hello",
                    "field": self.custom_field_1.id,
                },
                {
                    "content": "HELLO 2",
                    "field": self.custom_field_2.id,
                },
            ],
        }

        response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.DataElement.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Make sure we actually created data.
        self.assertEqual(len(response.data['customvalue_set']), 2)  # Make sure we have 2 custom value objects.
        self.assertEqual(response.data['workgroup'], self.wg.id)

    def test_api_list_or_create_metadata_post_request_for_value_domain_with_subcomponents(self):

        dt = mdr_models.DataType.objects.create(name="Test DT", workgroup=self.wg)

        post_data = {
            "name": "My Value Domain",
            "definition": "My Value Domain definition",
            "stewardship_organisation": self.so.id,
            "workgroup": self.wg.id,
            "submitter": None,
            "version": "",
            "references": "These are my references",
            "origin_URI": "",
            "origin": "This is my origin",
            "comments": "My comments",
            "data_type": dt.id,
            "format": "N",
            "maximum_length": 1,
            "unit_of_measure": None,
            "conceptual_domain": None,
            "description": "",
            "permissiblevalue_set": [
                {
                    "value": "0",
                    "meaning": "My meaning",
                    "order": 1,
                    "start_date": "2018-01-01",
                },
                {
                    "value": "1",
                    "meaning": "My meaning 1",
                    "order": 2,
                    "start_date": "2018-02-02",
                },
            ],
            "supplementaryvalue_set": [
                {
                    "value": "s0",
                    "meaning": "My meaning sv",
                    "order": 1,
                    "start_date": "2018-01-01",
                },
                {
                    "value": "s1",
                    "meaning": "My meaning sv 1",
                    "order": 2,
                    "start_date": "2018-02-02",
                }
            ],
            "slots": [],
            "customvalue_set": [
                {
                    "field": self.custom_field_1.id,
                    "name": "New Name 1",
                    "content": "Activity - need for assistance",
                },
                {
                    "field": self.custom_field_2.id,
                    "name": "New Name 2",
                    "content": "",
                },
            ],
            "org_records": [],
            "identifiers": []
        }

        response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.ValueDomain.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Make sure we actually created data.
        self.assertEqual(len(response.data['supplementaryvalue_set']), 2)  # We have 2 supplementary value objects.
        self.assertEqual(len(response.data['permissiblevalue_set']), 2)  # We have 2 permissible value objects.
