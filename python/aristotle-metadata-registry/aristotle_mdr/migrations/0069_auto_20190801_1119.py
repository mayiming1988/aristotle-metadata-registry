# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-01 01:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0067_auto_20190605_1538'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='permissiblevalue',
            options={'verbose_name': 'Permissible Value'},
        ),
        migrations.AlterModelOptions(
            name='supplementaryvalue',
            options={'verbose_name': 'Supplementary Value'},
        ),
    ]
