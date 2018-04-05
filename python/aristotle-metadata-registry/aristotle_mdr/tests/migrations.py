from django.apps import apps as nowapps
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from django.test import TestCase
from django.test.testcases import TransactionTestCase
import unittest

# This is an object so it is not run as a test. See usage in main.test_migrations
@unittest.skipIf(connection.vendor in ['microsoft', 'mssql'], "MSSQL Doesn't support temporarily disabling foreign key constraints")
class MigrationsTestCase(object):
    """
    Thanks to: https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    """

    @property
    def app(self):
        return nowapps.get_containing_app_config(type(self).__module__).name

    migrate_from = None
    migrate_to = None

    def setUp(self):
        assert self.migrate_from and self.migrate_to, \
            "TestCase '{}' must define migrate_from and migrate_to properties".format(type(self).__name__)
        self.migrate_from = [(self.app, self.migrate_from)]
        self.migrate_to = [(self.app, self.migrate_to)]
        executor = MigrationExecutor(connection)
        #print('unmigrated: %s'%executor.loader.unmigrated_apps)
        #print('migrated: %s'%executor.loader.migrated_apps)

        #executor.loader.build_graph()  # reload.
        old_apps = executor.loader.project_state(self.migrate_from).apps

        executor.migrate(self.migrate_from)

        self.setUpBeforeMigration(old_apps)

        # Run the migration to test
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(self.migrate_to)

        self.apps = executor.loader.project_state(self.migrate_to).apps

    def setUpBeforeMigration(self, apps):
        pass
