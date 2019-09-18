from aristotle_mdr import models
from aristotle_mdr.contrib.slots import models as slots_models
from aristotle_mdr.models import STATES
from aristotle_mdr.tests.migrations import MigrationsTestCase
from aristotle_mdr.utils import migrations as migration_utils

from django.test import TestCase, tag
from django.apps import apps as current_apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.management import create_contenttypes
from django.utils import timezone
from unittest import skip


class TestMoveImplementationDateMigration(MigrationsTestCase, TestCase):

    app = 'aristotle_dse'
    migrate_from = [
        ('aristotle_mdr', '0057_auto_20190329_1609'),
        ('aristotle_dse', '0021_auto_20190415_0012'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]
    migrate_to = [
        ('aristotle_dse','0022_auto_20190501_1043')
    ]

    def setUpBeforeMigration(self, apps):
        # Below forces content types to be created for the migrated items
        from django.contrib.contenttypes.management import create_contenttypes
        app_config = apps.get_app_config('aristotle_dse')
        app_config.models_module = app_config.models_module or True
        create_contenttypes(app_config)

        app_config = apps.get_app_config('aristotle_dse')
        app_config.models_module = app_config.models_module or True
        create_contenttypes(app_config)

        DataSetSpecification = apps.get_model('aristotle_dse', 'DataSetSpecification')

        self.implementation_start_date="2018-01-01"
        self.implementation_end_date="2019-01-01"

        self.dss = DataSetSpecification.objects.create(
            name='My DSS',
            definition='test defn',
            implementation_start_date=self.implementation_start_date,
            implementation_end_date=self.implementation_end_date,
        )

    def test_migration(self):
        apps = self.apps
        # Below forces content types to be created for the migrated items
        from django.contrib.contenttypes.management import create_contenttypes
        app_config = apps.get_app_config('aristotle_dse')
        app_config.models_module = app_config.models_module or True
        create_contenttypes(app_config)

        DataSetSpecification = self.apps.get_model('aristotle_dse', 'DataSetSpecification')
        CustomField = self.apps.get_model('aristotle_mdr_custom_fields', 'CustomField')
        ContentType = self.apps.get_model('contenttypes', 'ContentType')
        CustomValue = self.apps.get_model('aristotle_mdr_custom_fields', 'CustomValue')

        ctype = ContentType.objects.get(
            app_label='aristotle_dse',
            model='datasetspecification',
        )

        self.dss = DataSetSpecification.objects.get(pk=self.dss.pk)

        isd_field = CustomField.objects.get(
            name="Implementation Start Date",
            allowed_model=ctype,
        )
        ied_field = CustomField.objects.get(
            name="Implementation End Date",
            allowed_model=ctype,
        )
        
        self.assertEqual('date', isd_field.type)
        self.assertEqual('date', ied_field.type)

        isd_value = CustomValue.objects.get(field=isd_field, concept=self.dss)
        ied_value = CustomValue.objects.get(field=ied_field, concept=self.dss)

        self.assertEqual(isd_value.content, self.implementation_start_date)
        self.assertEqual(ied_value.content, self.implementation_end_date)
