from django.urls import reverse

from aristotle_mdr import models as mdr_models
from aristotle_mdr_api.v4.tests import BaseAPITestCase
from django.conf import settings


import reversion

import logging
logger = logging.getLogger(__name__)

class ConceptAPITestCase(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.item = mdr_models.ObjectClass.objects.create(
            name='Test Concept',
            definition='Concept Definition',
            submitter=self.user
        )
        self.concept = self.item._concept_ptr

        # Create a new item without version permissions
        with reversion.revisions.create_revision():
            self.reversion_item_without_permissions = mdr_models.ObjectClass.objects.create(
                name="A published item",
                definition="test",
                submitter=self.submitting_user
            )
            reversion.revisions.set_comment("First edit")

        raise ValueError(self.reversion_item_without_permissions)





    def test_get_concept(self):
        self.login_user()
        response = self.client.get(
            reverse('api_v4:item:item', args=[self.concept.id]),
        )
        self.assertEqual(response.status_code, 200)

    def test_supersedes_graph(self):
        self.steward_org_1 = mdr_models.StewardOrganisation.objects.create(
            name="Test SO"
        )
        self.superseded_item = mdr_models.DataElementConcept.objects.create(
            name="SUPERSEDED ITEM",
            submitter=self.user
        )

        self.superseding_item = mdr_models.DataElementConcept.objects.create(
            name="SUPERSEDING ITEM",
            submitter=self.user
        )
        self.ra = mdr_models.RegistrationAuthority.objects.create(
            name="Test RA",
            stewardship_organisation=self.steward_org_1
        )

        mdr_models.SupersedeRelationship.objects.create(
            older_item=self.superseded_item,
            newer_item=self.superseding_item,
            registration_authority=self.ra
        )

        self.login_user()
        response = self.client.get(
            reverse('api_v4:item:item_supersedes_graphical', args=[self.superseded_item.id])
        )
        self.assertEqual(len(response.data['nodes']), 2)
        self.assertEqual(len(response.data['edges']), 1)

    def test_general_graph_number_of_nodes(self):

        self.maximum_number_of_nodes = settings.MAXIMUM_NUMBER_OF_NODES_IN_GENERAL_GRAPHICAL_REPRESENTATION

        for i in range(settings.MAXIMUM_NUMBER_OF_NODES_IN_GENERAL_GRAPHICAL_REPRESENTATION):
            mdr_models.DataElementConcept.objects.create(
                name="TEST DATA ELEMENT CONCEPT",
                definition="I like to be with the popular Concept",
                objectClass=self.item,
                submitter=self.user,
            )

        self.assertEqual(len(mdr_models.DataElementConcept.objects.all()),
                         settings.MAXIMUM_NUMBER_OF_NODES_IN_GENERAL_GRAPHICAL_REPRESENTATION)

        self.login_user()
        response = self.client.get(
            reverse('api_v4:item:item_general_graphical', args=[self.item.id])
        )

        self.assertEqual(len(response.data['nodes']), self.maximum_number_of_nodes)
        self.assertEqual(len(response.data['edges']), self.maximum_number_of_nodes - 1)

        # Create an extra DataElementConcept attached to the same item
        mdr_models.DataElementConcept.objects.create(
            name="TEST DATA ELEMENT CONCEPT",
            definition="I like to be with the popular Concept",
            objectClass=self.item,
            submitter=self.user,
        )

        response2 = self.client.get(
            reverse('api_v4:item:item_general_graphical', args=[self.item.id])
        )
        # The number of nodes and edges has to remain the same:
        self.assertEqual(len(response2.data['nodes']), self.maximum_number_of_nodes)
        self.assertEqual(len(response2.data['edges']), self.maximum_number_of_nodes - 1)

    def test_updating_version_permissions(self):
        pass

