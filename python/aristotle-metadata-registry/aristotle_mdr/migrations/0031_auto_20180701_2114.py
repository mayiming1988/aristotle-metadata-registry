# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-02 02:14
from __future__ import unicode_literals

import aristotle_mdr.fields
import autoslug.fields
import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


from aristotle_mdr.utils.migrations import (
    classproperty,
    StewardMigration
)


class Migration(StewardMigration):

    dependencies = [
        ('aristotle_mdr', '0030_auto_20180621_0217'),
    ]

    @classproperty
    def operations(cls):
        return [
        migrations.CreateModel(
            name='OrganisationAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', autoslug.fields.AutoSlugField(editable=True, populate_from='name')),
                ('name', models.TextField(help_text='The primary name used for human identification purposes.')),
                ('uuid', models.UUIDField(default=uuid.uuid1, editable=False, unique=True)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition')),
            ],
            options={
                'verbose_name': 'Organisation',
            },
        ),
        migrations.CreateModel(
            name='OrganisationAccountMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('steward', 'Steward'), ('member', 'Member')], help_text='Role within this group', max_length=128)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='aristotle_mdr.OrganisationAccount', to_field='uuid')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='organisationaccountmembership',
            unique_together=set([('user', 'group')]),
        ),
            migrations.RunPython(cls.add_stewardship_org, migrations.RunPython.noop),
    ]
