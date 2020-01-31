# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-20 02:04
from __future__ import unicode_literals

import aristotle_mdr.fields
import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid

from aristotle_mdr.utils.migration_utils import (
    classproperty,
    StewardMigration
)


def populate_names(apps, schema_migration):
    from django.db.models import F
    Namespace = apps.get_model('aristotle_mdr_identifiers', 'Namespace')
    Namespace.objects.all().update(name=F('shorthand_prefix'))


class Migration(StewardMigration):

    dependencies = [
        ('aristotle_mdr', '0056_auto_20190313_2144'),
        ('aristotle_mdr_identifiers', '0005_auto_20180624_2049'),
    ]
    # stewardorganisation = None

    @classproperty
    def operations(klass):
        return [
            migrations.RunPython(klass.fetch_stewardship_org_uuid, migrations.RunPython.noop),
            migrations.RemoveField(
                model_name='namespace',
                name='naming_authority',
            ),
            migrations.AddField(
                model_name='namespace',
                name='definition',
                field=ckeditor_uploader.fields.RichTextUploadingField(default="", help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
                preserve_default=False,
            ),
            migrations.AddField(
                model_name='namespace',
                name='name',
                field=aristotle_mdr.fields.ShortTextField(default="Name", help_text='The primary name used for human identification purposes.'),
                preserve_default=False,
            ),
            migrations.AddField(
                model_name='namespace',
                name='stewardship_organisation',
                field=models.ForeignKey(default=klass.get_uuid, on_delete=django.db.models.deletion.CASCADE, to='aristotle_mdr.StewardOrganisation', to_field='uuid'),
                preserve_default=False,
            ),
            migrations.AddField(
                model_name='namespace',
                name='uuid',
                field=models.UUIDField(default=uuid.uuid1, editable=False, help_text='Universally-unique Identifier. Uses UUID1 as this improves uniqueness and tracking between registries', unique=True),
            ),
            migrations.RunPython(populate_names, migrations.RunPython.noop),
        ]