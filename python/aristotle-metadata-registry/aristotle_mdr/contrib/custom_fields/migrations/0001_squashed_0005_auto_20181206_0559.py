# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-10 23:36
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aristotle_mdr', '0046_auto_20181107_0433'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=1000)),
                ('type', models.CharField(choices=[('int', 'Integer'), ('str', 'String'), ('html', 'Rich Text'), ('date', 'Date')], max_length=10)),
                ('help_text', models.CharField(max_length=1000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('content', models.TextField()),
                ('concept', aristotle_mdr.fields.ConceptForeignKey(on_delete=django.db.models.deletion.CASCADE, on_delete=django.db.models.deletion.CASCADE, to=on_delete=django.db.models.deletion.CASCADE'aristotle_mdr._concept')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, on_delete=django.db.models.deletion.CASCADE, to=on_delete=django.db.models.deletion.CASCADE'aristotle_mdr_custom_fields.CustomField')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='customfield',
            name='order',
            field=models.IntegerField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customfield',
            name='help_text',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='name',
            field=models.CharField(max_length=1000, unique=True),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='type',
            field=models.CharField(choices=[('int', 'Integer'), ('str', 'Text'), ('html', 'Rich Text'), ('date', 'Date')], max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='customvalue',
            unique_together=set([('field', 'concept')]),
        ),
        migrations.AddField(
            model_name='customfield',
            name='allowed_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, on_delete=django.db.models.deletion.CASCADE, to=on_delete=django.db.models.deletion.CASCADE'contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='customfield',
            name='visibility',
            field=models.IntegerField(choices=[(0, 'Public'), (1, 'Authenticated'), (2, 'Workgroup')], default=0),
        ),
        migrations.AlterModelOptions(
            name='customfield',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='customvalue',
            options={'ordering': ['field__order']},
        ),
        migrations.AlterField(
            model_name='customvalue',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', on_delete=django.db.models.deletion.CASCADE, to=on_delete=django.db.models.deletion.CASCADE'aristotle_mdr_custom_fields.CustomField'),
        ),
    ]
