# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-16 00:23
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0046_auto_20181107_0433'),
        ('aristotle_mdr_links', '0005_switch_to_concept_relations'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='root_item',
            field=aristotle_mdr.fields.ConceptForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owned_links', to='aristotle_mdr._concept'),
        ),
    ]
