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
            submitter=self.user
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
            reverse('api_v4:metadata:generic_metadata_serialiser_api_endpoint',
                    kwargs={
                        "item_uuid": self.item.uuid,
                        "metadata_type": self.item.item_type.model,
                    }
                    ),
        )

    def test_api_redirection_works(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_api_serialiser_works_and_fields_are_shown(self):
        self.assertDictEqual(
            {"name": self.item.name, "definition": self.item.definition},
            {"name": self.response.data['name'], "definition": self.response.data['definition']}
        )
