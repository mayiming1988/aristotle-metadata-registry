# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-18 02:44
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr_backwards', '__first__'),
        ('aristotle_mdr', '0049_make_non_nullable_so'),
    ]

    operations = [
        migrations.AddField(
            model_name='valuedomain',
            name='classification_scheme',
            field=aristotle_mdr.fields.ConceptForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='valueDomains', to='aristotle_mdr_backwards.ClassificationScheme', verbose_name='Classification Scheme'),
        ),
    ]
