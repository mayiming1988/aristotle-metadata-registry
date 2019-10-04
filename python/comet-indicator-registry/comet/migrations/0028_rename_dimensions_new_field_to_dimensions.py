from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('comet', '0027_auto_20191003_0123'),
        ('aristotle_mdr', '0081_remove_rename_and_alter_abstractvalue_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='indicator',
            old_name='dimensions_new',
            new_name='dimensions',
        ),
    ]
