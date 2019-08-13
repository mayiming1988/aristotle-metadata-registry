# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-29 01:43
from __future__ import unicode_literals

import aristotle_mdr.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr', '0030_auto_20180621_0217'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationauthority',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='possumprofile',
            name='profilePicture',
            field=aristotle_mdr.fields.ConvertedConstrainedImageField(blank=True, content_types=['image/jpg', 'image/png', 'image/bmp', 'image/jpeg'], height_field='profilePictureHeight', js_checker=True, max_upload_size=10485760, mime_lookup_length=4096, null=True, upload_on_delete=django.db.models.deletion.CASCADE, to='', width_field='profilePictureWidth'),
        ),
    ]
