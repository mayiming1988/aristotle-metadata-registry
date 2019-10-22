# Generated by Django 2.2.5 on 2019-10-09 01:30

from django.db import migrations, models
import aristotle_mdr.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aristotle_dse', '0039_remove_dssgrouping_linked_group'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dssgrouping',
            old_name='linked_group_new',
            new_name='linked_group',
        ),
        migrations.RenameField(
            model_name='dssdeinclusion',
            old_name='specialisation_classes_new',
            new_name='specialisation_classes',
        ),

        # Remove Related names:
        migrations.AlterField(
            model_name='dssgrouping',
            name='linked_group',
            field=models.ManyToManyField(
                blank=True,
                through='aristotle_dse.DSSGroupingLinkedGroupThrough',
                to='aristotle_dse.DSSGrouping'),
        ),
        migrations.AlterField(
            model_name='dssdeinclusion',
            name='specialisation_classes',
            field=aristotle_mdr.fields.ConceptManyToManyField(
                blank=True,
                through='aristotle_dse.DSSDEInclusionSpecialisationClassesThrough',
                to='aristotle_mdr.ObjectClass'),
        ),

    ]
