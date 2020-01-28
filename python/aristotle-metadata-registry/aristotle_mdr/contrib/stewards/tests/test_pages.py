from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from aristotle_mdr import models as mdr_models
from aristotle_mdr.models import StewardOrganisation
from aristotle_mdr.contrib.stewards.tests.test_perms import BaseStewardOrgsTestCase
from aristotle_mdr.contrib.stewards.models import Collection
from aristotle_mdr.contrib.publishing.models import PublicationRecord
from aristotle_mdr.contrib.aristotle_backwards.models import RepresentationClass
from aristotle_mdr.contrib.identifiers.models import Namespace


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
            stewardship_organisation=self.steward_org_1,
            name='My Base Collection',
        )
        PublicationRecord.objects.create(
            content_type=ContentType.objects.get_for_model(Collection),
            object_id=self.collection.id,
            publisher=self.org_manager,
        )

        # Create third SO with member
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
        PublicationRecord.objects.create(
            content_type=ContentType.objects.get_for_model(Collection),
            object_id=self.new_org_collection.id,
            publisher=self.new_org_member,
        )

    def test_view_collection(self):
        """Test viewing a collection"""
        self.login_oscar()

        view_args = [self.steward_org_1.slug, self.collection.id]
        response = self.client.get(
            reverse('aristotle:stewards:group:collection_detail_view', args=view_args)
        )

        self.assertEqual(response.status_code, 200)

    def test_load_create_collections(self):
        """Test loading the create collection page when a memeber of the SO"""
        self.login_oscar()

        response = self.client.get(
            reverse('aristotle:stewards:group:collections_create', args=[self.steward_org_1.slug])
        )

        self.assertEqual(response.status_code, 200)

    def test_load_create_sub_collection(self):
        """Test loading the create sub collection page"""
        self.login_oscar()
        response = self.client.get(
            reverse(
                'aristotle:stewards:group:sub_collections_create',
                args=[self.steward_org_1.slug, self.collection.id]
            ),
        )

        self.assertEqual(response.status_code, 200)

    def test_create_collection_with_parent(self):
        """Test creating a collection with a valid parent"""
        self.login_oscar()

        collection_name = 'My new collection'
        data = {
            'name': collection_name,
            'description': 'A very new collection',
        }

        response = self.client.post(
            reverse(
                'aristotle:stewards:group:sub_collections_create',
                args=[self.steward_org_1.slug, self.collection.id]
            ),
            data
        )

        self.assertEqual(response.status_code, 302)

        new_collection = Collection.objects.get(name=collection_name)
        self.assertEqual(new_collection.parent_collection, self.collection)

    def test_create_collection_with_other_so_parent(self):
        """Test creating a collection with a parent in another stewardship org"""
        self.login_oscar()

        collection_name = 'A bad collection'
        data = {
            'name': collection_name,
            'description': 'Not legit',
        }

        response = self.client.post(
            reverse(
                'aristotle:stewards:group:sub_collections_create',
                args=[self.steward_org_1.slug, self.new_org_collection.id]
            ),
            data
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Collection.objects.filter(name=collection_name).count(),
            0
        )

    def test_move_collection(self):
        """Test changing the parent of a collection"""
        self.login_oscar()

        parent = Collection.objects.create(
            stewardship_organisation=self.steward_org_1,
            name='Parent Collection',
        )

        self.assertIsNone(self.collection.parent_collection)

        data = {
            'parent_collection': parent.id
        }
        response = self.client.post(
            reverse(
                'aristotle:stewards:group:collection_move_view',
                args=[self.steward_org_1.slug, self.collection.id]
            ),
            data
        )

        self.assertEqual(response.status_code, 302)

        self.collection.refresh_from_db()
        self.assertEqual(self.collection.parent_collection, parent)

    def test_move_collection_into_itself(self):
        """Test that making a collection a child of itself is not allowed"""
        self.login_oscar()

        self.assertIsNone(self.collection.parent_collection)

        data = {
            'parent_collection': self.collection.id
        }
        response = self.client.post(
            reverse(
                'aristotle:stewards:group:collection_move_view',
                args=[self.steward_org_1.slug, self.collection.id]
            ),
            data
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue('parent_collection' in response.context['form'].errors)

    def test_edit_collection(self):
        """Test editing an existing collection"""
        self.login_oscar()

        new_name = 'Very Edited Name'
        new_description = 'Very Edited Description'
        data = {
            'name': new_name,
            'description': new_description
        }
        response = self.client.post(
            reverse(
                'aristotle:stewards:group:collection_edit_view',
                args=[self.steward_org_1.slug, self.collection.id]
            ),
            data
        )

        self.assertEqual(response.status_code, 302)

        self.collection.refresh_from_db()
        self.assertEqual(self.collection.name, new_name)
        self.assertEqual(self.collection.description, new_description)

    def test_edit_collection_without_perm(self):
        """Test that editing fails if not a steward or admin of the Stewardship Organisation"""
        self.login_frankie()

        data = {
            'name': 'Bad',
            'description': 'Bad'
        }
        response = self.client.post(
            reverse(
                'aristotle:stewards:group:collection_edit_view',
                args=[self.steward_org_1.slug, self.collection.id]
            ),
            data
        )

        self.assertEqual(response.status_code, 403)


class ManagedItemTestCase(BaseStewardOrgsTestCase, TestCase):

    def setUp(self):
        super().setUp()

        # Create some test managed items
        self.namespace = Namespace.objects.create(
            name='Test Namespace',
            definition='For testing',
            stewardship_organisation=self.steward_org_1,
        )
        self.metres = mdr_models.Measure.objects.create(
            name='Metres',
            definition='Like, pretty long aye',
            stewardship_organisation=self.steward_org_1,
        )
        self.centimetres = mdr_models.Measure.objects.create(
            name='Centimetres',
            definition='Like metres but smaller',
            stewardship_organisation=self.steward_org_1,
        )
        self.time = RepresentationClass.objects.create(
            name='Time',
            definition='A point in spacetime',
            stewardship_organisation=self.steward_org_1,
        )

    def test_load_managed_item_create(self):
        self.login_oscar()
        response = self.client.get(
            reverse('aristotle:stewards:group:create_managed_item',
                    args=[self.steward_org_1.slug, 'measure'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_load_managed_item_create_anon(self):
        response = self.client.get(
            reverse('aristotle:stewards:group:create_managed_item',
                    args=[self.steward_org_1.slug, 'measure'])
        )
        self.assertEqual(response.status_code, 403)

    def test_managed_item_create(self):
        """Test that an SO manager can create an item"""
        self.login_oscar()
        definition = 'Like metres but bigger'
        data = {
            'name': 'Kilometres',
            'definition': definition,
            'stewardship_organisation': self.steward_org_1.uuid
        }

        response = self.client.post(
            reverse(
                'aristotle:stewards:group:create_managed_item',
                args=[self.steward_org_1.slug, 'measure']
            ),
            data
        )
        self.assertEqual(response.status_code, 302)

        measure = mdr_models.Measure.objects.filter(name='Kilometres')
        self.assertEqual(measure.count(), 1)

        kilometres = measure[0]
        self.assertEqual(kilometres.definition, definition)
        self.assertEqual(kilometres.stewardship_organisation, self.steward_org_1)

    def test_load_managed_item_edit(self):
        """Test that a SO manager can edit a managed item"""
        self.login_oscar()
        response = self.client.get(
            reverse(
                'aristotle:stewards:group:edit_managed_item',
                args=[self.steward_org_1.slug, 'measure', self.centimetres.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

    def test_load_managed_item_edit_anon(self):
        """Test that an anonymous user cannot load the edit managed item form"""
        response = self.client.get(
            reverse(
                'aristotle:stewards:group:edit_managed_item',
                args=[self.steward_org_1.slug, 'measure', self.centimetres.id]
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_managed_item_edit(self):
        """Test that a SO manager can edit a managed item"""
        self.login_oscar()
        new_definition = 'Like real small'
        data = {
            'name': self.centimetres.name,
            'definition': new_definition,
            'stewardship_organisation': self.centimetres.stewardship_organisation
        }

        response = self.client.post(
            reverse(
                'aristotle:stewards:group:edit_managed_item',
                args=[self.steward_org_1.slug, 'measure', self.centimetres.id]
            ),
            data
        )
        self.assertEqual(response.status_code, 302)

        self.centimetres.refresh_from_db()
        self.assertEqual(self.centimetres.name, 'Centimetres')
        self.assertEqual(self.centimetres.definition, new_definition)
        self.assertEqual(self.centimetres.stewardship_organisation, self.steward_org_1)

    def test_view_managed_item_types(self):
        """Test that an anonymous user can view managed item types"""
        response = self.client.get(
            reverse('aristotle:stewards:group:managed_item_list_types', args=[self.steward_org_1.slug])
        )
        self.assertEqual(response.status_code, 200)
        # Check that there are types in list
        self.assertTrue(len(response.context['object_list']) > 1)

    def test_view_managed_item_list(self):
        """Test that a SO manager can view managed item list"""
        self.login_oscar()
        response = self.client.get(
            reverse(
                'aristotle:stewards:group:managed_item_list_items',
                args=[self.steward_org_1.slug, 'measure']
            )
        )
        self.assertEqual(response.status_code, 200)

        expected = [
            self.centimetres,
            self.metres
        ]
        self.assertCountEqual(response.context['object_list'], expected)
