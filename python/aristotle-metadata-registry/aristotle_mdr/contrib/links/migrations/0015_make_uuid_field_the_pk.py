# Generated by Django 2.2.5 on 2019-10-16 05:01

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr_links', '0014_copy_and_paste_foreign_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='linkend',
            name='role'
        ),
        migrations.RemoveField(
            model_name='relationrole',
            name='id',
        ),
        migrations.AlterField(
            model_name='relationrole',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid1, editable=False, help_text='Universally-unique Identifier. Uses UUID1 as this improves uniqueness and tracking between registries', primary_key=True, serialize=False, unique=True),
        ),
    ]