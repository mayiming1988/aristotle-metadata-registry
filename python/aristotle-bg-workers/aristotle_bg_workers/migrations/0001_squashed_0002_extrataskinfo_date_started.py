# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-21 04:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_results', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraTaskInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=100)),
                ('task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='extrainfo', on_delete=django.db.models.deletion.CASCADE, to=on_delete=django.db.models.deletion.CASCADE'django_celery_results.TaskResult')),
                ('task_creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, on_delete=django.db.models.deletion.CASCADE, to=on_delete=django.db.models.deletion.CASCADEsettings.AUTH_USER_MODEL)),
                ('date_started', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
