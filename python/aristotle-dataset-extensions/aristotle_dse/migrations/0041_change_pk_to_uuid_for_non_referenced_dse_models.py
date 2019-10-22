# Generated by Django 2.2.5 on 2019-10-17 05:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_dse', '0040_auto_20191008_2030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distributiondataelementpath',
            name='id',
        ),
        migrations.RemoveField(
            model_name='dssclusterinclusion',
            name='id',
        ),
        # migrations.RemoveField(
        #     model_name='dssdeinclusion',
        #     name='id',
        # ),
        migrations.AlterField(
            model_name='distributiondataelementpath',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid1, editable=False, help_text='Universally-unique Identifier. Uses UUID1 as this improves uniqueness and tracking between registries', primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='dssclusterinclusion',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid1, editable=False, help_text='Universally-unique Identifier. Uses UUID1 as this improves uniqueness and tracking between registries', primary_key=True, serialize=False, unique=True),
        ),
        # migrations.AlterField(
        #     model_name='dssdeinclusion',
        #     name='uuid',
        #     field=models.UUIDField(default=uuid.uuid1, editable=False, help_text='Universally-unique Identifier. Uses UUID1 as this improves uniqueness and tracking between registries', primary_key=True, serialize=False, unique=True),
        # ),
    ]
