# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-21 03:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AristotleToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('name', models.CharField(default='Token', max_length=100)),
                ('key', models.CharField(max_length=40, unique=True, verbose_name='Key')),
                ('permissions', jsonfield.fields.JSONField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', on_delete=django.db.models.deletion.CASCADE, to=on_delete=django.db.models.deletion.CASCADEsettings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
                'abstract': False,
            },
        ),
    ]
