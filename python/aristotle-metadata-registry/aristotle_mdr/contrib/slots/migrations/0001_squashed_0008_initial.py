# Generated by Django 2.2.6 on 2019-11-11 03:42

import aristotle_mdr.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aristotle_mdr', '0075_auto_20190916_1602'),
    ]

    replaces = [
        ('aristotle_mdr_slots', '0001_initial'),
        ('aristotle_mdr_slots', '0002_lengthen_slot_value'),
        ('aristotle_mdr_slots', '0003_correct_slots'),
        ('aristotle_mdr_slots', '0004_switch_to_concept_relations'),
        ('aristotle_mdr_slots', '0005_slot_order'),
        ('aristotle_mdr_slots', '0006_auto_20180531_0337'),
        ('aristotle_mdr_slots', '0007_auto_20180624_2049'),
        ('aristotle_mdr_slots', '0008_auto_20190711_0117'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=256)),
                ('type', models.CharField(blank=True, max_length=256)),
                ('value', models.TextField()),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Position')),
                ('permission', models.IntegerField(choices=[(0, 'Public'), (1, 'Authenticated'), (2, 'Workgroup'), (10, 'Registry Administrators')], default=0)),
                ('concept', aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slots', to='aristotle_mdr._concept')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
