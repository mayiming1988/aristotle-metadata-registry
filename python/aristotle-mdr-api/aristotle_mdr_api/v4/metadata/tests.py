from django.urls import reverse
from rest_framework import status
from aristotle_mdr_api.v4.tests import BaseAPITestCase
from aristotle_mdr import models as mdr_models


class ObjectCreationForMetadataAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        self.item = mdr_models.ObjectClass.objects.create(
            name='Test Concept',
            definition='Concept Definition',
            submitter=self.user,
        )

        self.login_user()


class MetadataRedirectionAPITestCase(ObjectCreationForMetadataAPITests):

    def setUp(self):
        super().setUp()
        self.response = self.client.get(
            reverse('api_v4:metadata:get_metadata_type_from_uuid', kwargs={"item_uuid": self.item.uuid}),
        )

    def test_get_metadata_type_redirection_works(self):
        self.assertEqual(self.response.status_code, status.HTTP_302_FOUND)

    def test_get_metadata_redirection_matches_object_uuid(self):
        self.assertTrue(str(self.item.uuid) in self.response.url.split("/"))

    def test_get_metadata_redirection_matches_object_type(self):
        self.assertTrue(self.item.item_type.model in self.response.url.split("/"))


class GenericMetadataSerialiserAPIViewTestCase(ObjectCreationForMetadataAPITests):

    def setUp(self):
        super().setUp()
        self.response = self.client.get(
            reverse(
                'api_v4:metadata:generic_metadata_serialiser_api_endpoint',
                kwargs={
                    "item_uuid": self.item.uuid,
                    "metadata_type": self.item.item_type.model,
                }
            ),
        )

    def test_api_response_status_is_200(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_api_serialiser_works_and_fields_are_shown(self):
        self.assertDictEqual(
            {"name": self.item.name, "definition": self.item.definition},
            {"name": self.response.data['name'], "definition": self.response.data['definition']},
        )


class ListOrCreateMetadataGetRequest(ObjectCreationForMetadataAPITests):

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

        self.response = self.client.get(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": self.value_domain_1.item_type.model,
                }
            ),
        )

    def test_api_list_or_create_metadata_get_request_response_status_is_200(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_api_list_or_create_metadata_get_request_returns_two_value_domain_objects(self):
        self.assertEqual(len(self.response.data['results']), 2)

    def test_api_list_or_create_metadata_get_request_paginator_returns_two_objects(self):
        self.assertEqual(self.response.data['count'], 2)

    def test_api_list_or_create_metadata_get_request_paginator_has_no_next(self):
        self.assertIsNone(self.response.data['next'])

    def test_api_list_or_create_metadata_get_request_paginator_has_no_previous(self):
        self.assertIsNone(self.response.data['previous'])


class ListOrCreateMetadataPostRequest(ObjectCreationForMetadataAPITests):

    def setUp(self):
        super().setUp()

        post_data = {
            "name": "Total Australian currency N[N(8)]",
            "definition": "Total number of Australian dollars.",
        }

        self.response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.ValueDomain.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )

    def test_api_list_or_create_metadata_post_request_response_status_is_201(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)


class ListOrCreateMetadataPostRequestWithForeignKeyIds(ObjectCreationForMetadataAPITests):

    def setUp(self):
        super().setUp()

        self.value_domain_1 = mdr_models.ValueDomain.objects.create(
            name='Test Value Domain 1',
            definition='VD Definition',
            submitter=self.user,
        )

        post_data = {
            "name": "MY TEST DATA ELEMENT",
            "definition": "DEFINITION FOR MY TEST DATA ELEMENT",
            "origin": "Blah blah...",
            "valueDomain": self.value_domain_1.id,
        }

        self.response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.DataElement.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )

    def test_metadata_api_creates_foreign_keys_from_id(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_metadata_api_data_is_correct(self):
        self.assertDictEqual(
            {"name": self.value_domain_1.id},
            {"name": self.response.data['valueDomain']},
        )


class ListOrCreateMetadataPostRequestWithSubComponentsAndComplexDataStructures(ObjectCreationForMetadataAPITests):

    def setUp(self):
        super().setUp()

        from aristotle_mdr.contrib.custom_fields.models import CustomField

        self.custom_field_1 = CustomField.objects.create(
            name="Test CustomField",
            order=1,
        )

        self.custom_field_2 = CustomField.objects.create(
            name="Test CustomField",
            order=2,
        )

        post_data = {
            "name": "MY DATA ELEMENT WITH CUSTOM VALUES",
            "definition": "THIS DATA ELEMENT HAS CUSTOM VALUES.",
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

        self.response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": mdr_models.DataElement.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )

    def test_api_list_or_create_metadata_post_request_response_status_is_201(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

