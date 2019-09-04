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
        self.assertEqual(post_data['name'], mdr_models.ValueDomain.objects.last().name)  # ValueDomain is in db.

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
        self.assertEqual(response.data['workgroup'], self.wg.id)  # Workgroup was actually saved.
        self.assertEqual(post_data['name'], mdr_models.DataElement.objects.last().name)  # Data Element is in db.

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

        my_saved_value_domain = mdr_models.ValueDomain.objects.last()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Make sure we actually created data.
        self.assertEqual(len(response.data['supplementaryvalue_set']), 2)  # We have 2 supplementary value objects.
        self.assertEqual(len(response.data['permissiblevalue_set']), 2)  # We have 2 permissible value objects.
        self.assertEqual(response.data['data_type'], dt.id)  # The DataType was actually saved.
        self.assertEqual(post_data['name'], my_saved_value_domain.name)  # ValueDomain is in db.
        self.assertEqual(post_data['permissiblevalue_set'][0]['value'], my_saved_value_domain.permissibleValues[0].value)
        self.assertEqual(post_data['permissiblevalue_set'][0]['meaning'], my_saved_value_domain.permissibleValues[0].meaning)
        self.assertEqual(post_data['permissiblevalue_set'][0]['order'], my_saved_value_domain.permissibleValues[0].order)
        self.assertEqual(post_data['permissiblevalue_set'][0]['start_date'], my_saved_value_domain.permissibleValues[0].start_date)
        self.assertEqual(post_data['permissiblevalue_set'][1]['value'], my_saved_value_domain.permissibleValues[1].value)
        self.assertEqual(post_data['permissiblevalue_set'][1]['meaning'], my_saved_value_domain.permissibleValues[1].meaning)
        self.assertEqual(post_data['permissiblevalue_set'][1]['order'], my_saved_value_domain.permissibleValues[1].order)
        self.assertEqual(post_data['permissiblevalue_set'][1]['start_date'], my_saved_value_domain.permissibleValues[1].start_date)

    def test_api_list_or_create_metadata_post_request_for_data_set_specification_with_subcomponents(self):

        from aristotle_dse.models import DataSetSpecification

        post_data = {
            "id": 5,
            "name": "My DSS",
            "definition": "This is my definition",
            "stewardship_organisation": "fef721d6c89e11e9bc630242ac12000b",
            "submitter": None,
            "version": "",
            "references": "",
            "origin_URI": "",
            "origin": "",
            "comments": "",
            "statistical_unit": None,
            "collection_method": "My collection method.",
            "groups": [],
            "dssdeinclusion_set": [
                {
                    "id": 33458,
                    "reference": "1",
                    "maximum_occurrences": 18,
                    "inclusion": "mandatory",
                    "specific_information": "This is my specific info.",
                    "conditional_inclusion": "",
                    "order": 0,
                    "data_element": 568962,
                    "group": None,
                    "specialisation_classes": []
                },
                {
                    "id": 33459,
                    "reference": "2",
                    "maximum_occurrences": 1,
                    "inclusion": "conditional",
                    "specific_information": "",
                    "conditional_inclusion": "My conditional inclusion.",
                    "order": 1,
                    "data_element": 568998,
                    "group": None,
                    "specialisation_classes": []
                },
                {
                    "id": 33460,
                    "reference": "3",
                    "maximum_occurrences": 2,
                    "inclusion": "conditional",
                    "specific_information": "",
                    "conditional_inclusion": "",
                    "order": 2,
                    "data_element": 569486,
                    "group": None,
                    "specialisation_classes": []
                },
                {
                    "id": 33461,
                    "reference": "4",
                    "maximum_occurrences": 24,
                    "inclusion": "mandatory",
                    "specific_information": "More than one substance use service may be selected.",
                    "conditional_inclusion": "",
                    "order": 3,
                    "data_element": 568907,
                    "group": None,
                    "specialisation_classes": []
                },
                {
                    "id": 33462,
                    "reference": "5",
                    "maximum_occurrences": 2,
                    "inclusion": "conditional",
                    "specific_information": "",
                    "conditional_inclusion": "This data element is cool.",
                    "order": 4,
                    "data_element": 568937,
                    "group": None,
                    "specialisation_classes": []
                }
            ],
            "dssclusterinclusion_set": [],
            "slots": [],
            "customvalue_set": [
                {
                    "field": 100,
                    "name": "Synonymous Name",
                    "content": "",
                    "id": 344213
                },
                {
                    "field": 101,
                    "name": "Short name",
                    "content": "",
                    "id": 344214
                },
                {
                    "field": 102,
                    "name": "Submitting Organisation",
                    "content": "My content",
                    "id": 344215
                },
                {
                    "field": 103,
                    "name": "Submitting Organisation Contact Details",
                    "content": "",
                    "id": 344216
                },
                {
                    "field": 104,
                    "name": "Steward Contact Details",
                    "content": "",
                    "id": 344217
                },
                {
                    "field": 105,
                    "name": "Context",
                    "content": "",
                    "id": 344218
                },
                {
                    "field": 106,
                    "name": "Guide for use",
                    "content": "",
                    "id": 344219
                },
                {
                    "field": 107,
                    "name": "Data Set Specification Type",
                    "content": "Data Element Cluster",
                    "id": 344220
                },
                {
                    "field": 110,
                    "name": "Statistical Unit",
                    "content": "",
                    "id": 344221
                },
                {
                    "field": 111,
                    "name": "Exclude From Dictionary",
                    "content": "",
                    "id": 344222
                }
            ],
            "org_records": [],
            "identifiers": []
        }

        response = self.client.post(
            reverse(
                'api_v4:metadata:list_or_create_metadata_endpoint',
                kwargs={
                    "metadata_type": DataSetSpecification.__name__.lower(),
                }
            ),
            post_data,
            format='json',
        )

        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Make sure we actually created data.
        # self.assertEqual(len(response.data['supplementaryvalue_set']), 2)  # We have 2 supplementary value objects.
        # self.assertEqual(len(response.data['permissiblevalue_set']), 2)  # We have 2 permissible value objects.
        # self.assertEqual(post_data['name'], mdr_models.ValueDomain.objects.last().name)  # ValueDomain is in db.
