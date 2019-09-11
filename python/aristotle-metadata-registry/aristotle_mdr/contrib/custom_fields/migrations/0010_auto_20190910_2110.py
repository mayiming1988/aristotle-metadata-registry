# Generated by Django 2.2.5 on 2019-09-11 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_mdr_custom_fields', '0009_auto_20190809_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='unique_name',
            field=models.CharField(help_text='A name used for uniquely identifying the custom field', max_length=1000, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='customfield',
            unique_together={('name', 'unique_name')},
        ),
    ]
