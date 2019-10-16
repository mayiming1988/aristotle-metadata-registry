from django.test import TestCase
from aristotle_mdr.tests.migration_test_utils import MigrationsTestCase


class TestRelationRolePrimaryKeyChange(MigrationsTestCase, TestCase):
    app = 'aristotle_mdr_links'

    migrate_from = [
        ('aristotle_mdr', '0084_auto_20191015_1736'),
        ('aristotle_mdr_links', '0013_add_temporary_field')
    ]
    migrate_to = '0014_copy_and_paste_foreign_value'

    def setUpBeforeMigration(self, apps):
        Link = apps.get_model('aristotle_mdr_links', 'link')
        LinkEnd = apps.get_model('aristotle_mdr_links', 'linkend')
        Relation = apps.get_model('aristotle_mdr_links', 'relation')
        RelationRole = apps.get_model('aristotle_mdr_links', 'relationrole')
        DataElement = apps.get_model('aristotle_mdr', 'dataelement')

        de1 = DataElement.objects.create(name="Test DE 1", definition="definition")
        de2 = DataElement.objects.create(name="Test DE 2", definition="definition")

        rel = Relation.objects.create(name="test_relation", definition="Used for testing")
        rel_role = RelationRole.objects.create(
            name="Relation Role Test", definition="test role", multiplicity=1,
            ordinal=2,
            relation=rel
        )
        link = Link.objects.create(relation=rel, root_item=de1)
        LinkEnd.objects.create(link=link, role=rel_role, concept=de2)
        # Make sure the temporary field is a UUID field:
        self.assertEqual(LinkEnd._meta.get_field('role_temp').get_internal_type(), 'UUIDField')
        # Make sure the LinkEnd object has a role assigned to it:
        le = LinkEnd.objects.last()
        self.assertEqual(le.role, rel_role)

    def test_migration(self):
        LinkEnd = self.apps.get_model('aristotle_mdr_links', 'linkend')
        RelationRole = self.apps.get_model('aristotle_mdr_links', 'relationrole')
        le = LinkEnd.objects.last()
        relation_role = RelationRole.objects.last()
        # Make sure the temporary uuid field has the value of the foreign key field:
        self.assertEqual(le.role_temp, relation_role.uuid)


class TestRelationRoleUUIDForeignKey(MigrationsTestCase, TestCase):
    app = 'aristotle_mdr_links'

    # migrate_from = [
    #     ('aristotle_mdr', '0084_auto_20191015_1736'),
    #     ('aristotle_mdr_links', '0016_add_foreign_key_field')
    # ]
    migrate_from = '0016_add_foreign_key_field'
    migrate_to = '0017_copy_and_paste_to_foreign_key'

    def setUpBeforeMigration(self, apps):
        Link = apps.get_model('aristotle_mdr_links', 'link')
        LinkEnd = apps.get_model('aristotle_mdr_links', 'linkend')
        Relation = apps.get_model('aristotle_mdr_links', 'relation')
        RelationRole = apps.get_model('aristotle_mdr_links', 'relationrole')
        DataElement = apps.get_model('aristotle_mdr', 'dataelement')

        de1 = DataElement.objects.create(name="Test DE 1", definition="definition")
        de2 = DataElement.objects.create(name="Test DE 2", definition="definition")

        rel = Relation.objects.create(name="test_relation", definition="Used for testing")
        rel_role = RelationRole.objects.create(
            name="Relation Role Test", definition="test role", multiplicity=1,
            ordinal=2,
            relation=rel
        )
        link = Link.objects.create(relation=rel, root_item=de1)
        LinkEnd.objects.create(link=link, role_temp=rel_role.uuid, concept=de2)
        # Make sure the new Field is a Foreign Key field:
        self.assertEqual(LinkEnd._meta.get_field('role').get_internal_type(), 'ForeignKey')

    def test_migration(self):
        Link = self.apps.get_model('aristotle_mdr_links', 'link')
        LinkEnd = self.apps.get_model('aristotle_mdr_links', 'linkend')
        Relation = self.apps.get_model('aristotle_mdr_links', 'relation')
        RelationRole = self.apps.get_model('aristotle_mdr_links', 'relationrole')
        DataElement = self.apps.get_model('aristotle_mdr', 'dataelement')
        le = LinkEnd.objects.last()
        relation_role = RelationRole.objects.last()

        self.assertEqual(le.role, relation_role)   # Check that new foreign key is working.
        self.assertTrue(LinkEnd._meta.get_field('role').is_relation)  # The new field is a foreign key (relation) field.
        self.assertEqual(le.role.uuid, relation_role.uuid)
