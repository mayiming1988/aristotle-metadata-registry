# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-09 02:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr_publishing', '0006_auto_20190711_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicationrecord',
            name='publisher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='published_content', to=settings.AUTH_USER_MODEL),
        ),
    ]