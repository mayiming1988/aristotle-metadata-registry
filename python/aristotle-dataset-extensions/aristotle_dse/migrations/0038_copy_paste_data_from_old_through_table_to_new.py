from django.db import migrations
from aristotle_mdr.utils.migration_utils import data_copy_and_paste_from_m2m_through_model


def copy_and_paste_data_from_old_through_table_to_new(apps, schema_editor):
    dssgrouping_model = apps.get_model('aristotle_dse', 'dssgrouping')
    through_model = apps.get_model('aristotle_dse', 'dssgroupinglinkedgroupthrough')
    data_copy_and_paste_from_m2m_through_model(dssgrouping_model, through_model, 'linked_group', with_self=True)


def copy_and_paste_data_from_new_through_table_to_old(apps, schema_editor):
    dssgrouping_model = apps.get_model('aristotle_dse', 'dssgrouping')
    through_model = apps.get_model('aristotle_dse', 'dssgrouping_linked_group')
    data_copy_and_paste_from_m2m_through_model(dssgrouping_model, through_model, 'linked_group_new', with_self=True)


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_dse', '0037_create_dssgrouping_new_through_table'),
    ]

    operations = [
        migrations.RunPython(copy_and_paste_data_from_old_through_table_to_new, reverse_code=copy_and_paste_data_from_new_through_table_to_old),
    ]
