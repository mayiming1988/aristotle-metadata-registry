from django.db import migrations
from aristotle_mdr.utils.migration_utils import data_copy_and_paste_foreign_value


def duplicate_models_foreign_keys(apps, schema_editor):
    permissible_value_model = apps.get_model('aristotle_mdr', 'permissiblevalue')
    supplementary_value_model = apps.get_model('aristotle_mdr', 'supplementaryvalue')
    data_copy_and_paste_foreign_value(permissible_value_model, 'value_meaning', 'uuid', 'value_meaning_new')
    data_copy_and_paste_foreign_value(supplementary_value_model, 'value_meaning', 'uuid', 'value_meaning_new')


class Migration(migrations.Migration):
    dependencies = [
        ('aristotle_mdr', '0079_auto_20191014_0055'),
    ]
    operations = [
        migrations.RunPython(duplicate_models_foreign_keys, reverse_code=migrations.RunPython.noop),
    ]
