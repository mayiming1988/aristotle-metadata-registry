from django.db import migrations
from aristotle_mdr.utils.migration_utils import data_copy_and_paste_foreign_value


def duplicate_models_foreign_keys(apps, schema_editor):
    PermissibleValue = apps.get_model('aristotle_mdr', 'permissiblevalue')
    SupplementaryValue = apps.get_model('aristotle_mdr', 'supplementaryvalue')
    data_copy_and_paste_foreign_value(PermissibleValue, 'value_meaning', 'uuid', 'value_meaning_temp')
    data_copy_and_paste_foreign_value(SupplementaryValue, 'value_meaning', 'uuid', 'value_meaning_temp')


class Migration(migrations.Migration):
    dependencies = [
        ('aristotle_mdr', '0079_auto_20191014_0055'),
    ]
    operations = [
        migrations.RunPython(duplicate_models_foreign_keys, reverse_code=migrations.RunPython.noop),
    ]
