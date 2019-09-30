from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_dse', '0034_dssdeinclusion_group_new'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dssdeinclusion',
            name='group',
        ),
    ]
