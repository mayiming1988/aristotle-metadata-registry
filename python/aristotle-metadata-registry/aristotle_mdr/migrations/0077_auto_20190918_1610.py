# Generated by Django 2.2.4 on 2019-09-18 06:10

from django.db import migrations
import uuid


def generate_uuids_for_dedderivesthrough(apps, schema_editor):
    model = apps.get_model('aristotle_mdr', 'dedderivesthrough')
    for row in model.objects.all():
        row.uuid = uuid.uuid1()
        row.save(update_fields=['uuid'])


def generate_uuids_for_dedinputsthrough(apps, schema_editor):
    model = apps.get_model('aristotle_mdr', 'dedinputsthrough')
    for row in model.objects.all():
        row.uuid = uuid.uuid1()
        row.save(update_fields=['uuid'])


def generate_uuids_for_permissiblevalue(apps, schema_editor):
    model = apps.get_model('aristotle_mdr', 'permissiblevalue')
    for row in model.objects.all():
        row.uuid = uuid.uuid1()
        row.save(update_fields=['uuid'])


def generate_uuids_for_supplementaryvalue(apps, schema_editor):
    model = apps.get_model('aristotle_mdr', 'supplementaryvalue')
    for row in model.objects.all():
        row.uuid = uuid.uuid1()
        row.save(update_fields=['uuid'])


def generate_uuids_for_valuemeaning(apps, schema_editor):
    model = apps.get_model('aristotle_mdr', 'valuemeaning')
    for row in model.objects.all():
        row.uuid = uuid.uuid1()
        row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0076_auto_20190918_1524'),
    ]

    operations = [
        migrations.RunPython(generate_uuids_for_dedderivesthrough, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(generate_uuids_for_dedinputsthrough, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(generate_uuids_for_permissiblevalue, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(generate_uuids_for_supplementaryvalue, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(generate_uuids_for_valuemeaning, reverse_code=migrations.RunPython.noop),
    ]
