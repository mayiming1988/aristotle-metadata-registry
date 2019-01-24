# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-18 05:20
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0050_valuedomain_classification_scheme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permissiblevalue',
            name='meaning',
            field=aristotle_mdr.fields.ShortTextField(blank=True, help_text="A textual designation of a value, where a relation to a Value meaning doesn't exist"),
        ),
        migrations.AlterField(
            model_name='supplementaryvalue',
            name='meaning',
            field=aristotle_mdr.fields.ShortTextField(blank=True, help_text="A textual designation of a value, where a relation to a Value meaning doesn't exist"),
        ),
    ]
