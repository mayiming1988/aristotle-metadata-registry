# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-07-11 06:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr_slots', '0007_auto_20180624_2049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='permission',
            field=models.IntegerField(choices=[(0, 'Public'), (1, 'Authenticated'), (2, 'Workgroup'), (10, 'Registry Administrators')], default=0),
        ),
    ]
