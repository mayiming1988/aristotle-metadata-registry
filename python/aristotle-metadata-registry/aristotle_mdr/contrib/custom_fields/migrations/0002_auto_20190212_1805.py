# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-13 00:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr_custom_fields', '0001_squashed_0005_auto_20181206_0559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='order',
            field=models.IntegerField(),
        ),
    ]
