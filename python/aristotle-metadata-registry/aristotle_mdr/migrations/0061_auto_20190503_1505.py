# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-03 05:05
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0060_organizationrecord_recordrelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='_concept',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='', help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='measure',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='', help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='', help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
        migrations.AlterField(
            model_name='organizationrecord',
            name='definition',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, default='', help_text='Representation of a concept by a descriptive statement which serves to differentiate it from related concepts. (3.2.39)', verbose_name='definition'),
        ),
    ]
