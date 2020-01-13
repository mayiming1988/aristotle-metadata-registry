from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from aristotle_mdr import models as mdr_models
from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.contrib.stewards.tests.test_perms import BaseStewardOrgsTestCase
from aristotle_mdr.contrib.stewards.models import Collection

User = get_user_model()


class OrgPagesTests(BaseStewardOrgsTestCase, TestCase):
    def setUp(self):
        super().setUp()

        self.item = mdr_models.ObjectClass.objects.create(
            name='Org 1',
            definition="1",
            stewardship_organisation=self.steward_org_1,
            workgroup=self.wg1
        )

        self.assertIn(
            self.item,
            mdr_models.ObjectClass.objects.visible(self.viewer),
        )

        self.ra.register(self.item, self.ra.public_state, self.su)

    def test_member_search(self):
        self.login_superuser()

        self.assertTrue(self.org_manager.stewardorganisationmembership_set.count() == 1)
        self.assertTrue(self.org_member_2.stewardorganisationmembership_set.count() == 1)

        org_manager_role = self.org_manager.stewardorganisationmembership_set.first()
        org_member_role = self.org_member_2.stewardorganisationmembership_set.first()

        member_search_url = reverse(
            "aristotle_mdr:stewards:group:member_list", args=[self.steward_org_1.slug]
        ) + "?user_filter={user}&role={role}"
        response = self.client.get(member_search_url.format(user="", role=""))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertTrue(org_member_role in response.context['object_list'])

        member_search_url = reverse(
            "aristotle_mdr:stewards:group:member_list", args=[self.steward_org_1.slug]
        ) + "?user_filter={user}&role_filter={role}"
        response = self.client.get(member_search_url.format(user="oscar", role=""))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertFalse(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="frank", role=""))
        self.assertFalse(org_manager_role in response.context['object_list'])
        self.assertTrue(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="", role=""))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertTrue(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="", role="admin"))
        self.assertTrue(org_manager_role in response.context['object_list'])
        self.assertFalse(org_member_role in response.context['object_list'])

        response = self.client.get(member_search_url.format(user="frankie", role="admin"))
        self.assertFalse(org_manager_role in response.context['object_list'])
        self.assertFalse(org_member_role in response.context['object_list'])


class CollectionsTestCase(BaseStewardOrgsTestCase, TestCase):

    def setUp(self):
        super().setUp()

        self.collection = Collection.objects.create(
            stewardship_organisation=self.steward_org_2,
            name='My Base Collection',
        )

        # Create second SO with member
        self.new_org = StewardOrganisation.objects.create(
            name='New org',
            description='Brand new',
            state=StewardOrganisation.states.active
        )

        self.new_org_member = User.objects.create_user(
            email='neworguser@example.com',
            short_name='NewUser',
            password='brand_new'
        )

        self.new_org.grant_role(
            role=StewardOrganisation.roles.member,
            user=self.new_org_member
        )

        self.new_org_collection = Collection.objects.create(
            stewardship_organisation=self.new_org,
            name='New orgs collection'
        )

    def test_load_create_collections(self):
        """Test loading the create collection page when a memeber of the SO"""
        self.login_oscar()

        response = self.client.get(
            reverse('aristotle:stewards:group:collections_create', args=[self.steward_org_1.slug])
        )

        self.assertEqual(response.status_code, 200)

    def test_create_collection_with_parent(self):
        """Test creating a collection with a valid parent"""
        self.login_oscar()

        collection_name = 'My new collection'
        data = {
            'name': collection_name,
            'description': 'A very new collection',
            'parent_collection': self.collection.id
        }

        response = self.client.post(
            reverse('aristotle:stewards:group:collections_create', args=[self.steward_org_1.slug]),
            data
        )

        self.assertEqual(response.status_code, 302)

        new_collection = Collection.objects.get(name=collection_name)
        self.assertEqual(new_collection.parent_collection, self.collection)

    def test_create_collection_with_invalid_parent(self):
        """Test creating a collection with a parent in another stewardship org"""
        self.login_oscar()

        collection_name = 'A bad collection'
        data = {
            'name': collection_name,
            'description': 'Not legit',
            'parent_collection': self.new_org_collection.id
        }

        response = self.client.post(
            reverse('aristotle:stewards:group:collections_create', args=[self.steward_org_1.slug]),
            data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Collection.objects.filter(name=collection_name).count(),
            0
        )
