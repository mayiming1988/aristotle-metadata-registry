from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_dse', '0035_remove_group_field'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dssdeinclusion',
            old_name='group_new',
            new_name='group',
        ),
    ]
