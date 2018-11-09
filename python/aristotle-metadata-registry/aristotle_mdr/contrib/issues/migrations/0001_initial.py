# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-01 04:04
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aristotle_mdr', '0045__concept_superseded_by_items'),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('description', models.TextField(blank=True)),
                ('isopen', models.BooleanField(default=True)),
                ('item', aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='aristotle_mdr._concept')),
            ],
        ),
    ]
