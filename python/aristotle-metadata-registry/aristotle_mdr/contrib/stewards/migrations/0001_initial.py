# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-07 09:24
from __future__ import unicode_literals

import aristotle_mdr.fields
import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aristotle_mdr', '0053_auto_20190226_0536'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', aristotle_mdr.fields.ShortTextField(help_text='The name of the group.')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='description')),
                ('metadata', aristotle_mdr.fields.ConceptManyToManyField(blank=True, to='aristotle_mdr._concept')),
                ('parent_collection', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='aristotle_mdr_stewards.Collection')),
                ('stewardship_organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aristotle_mdr.StewardOrganisation', to_field='uuid')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]