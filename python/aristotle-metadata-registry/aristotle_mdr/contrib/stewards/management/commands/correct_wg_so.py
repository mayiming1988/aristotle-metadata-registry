from django.core.management.base import BaseCommand
from aristotle_mdr.models import _concept


class Command(BaseCommand):
    help = 'Correctly assigns metadata in workgroups to the correct Steward Organisation.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def handle(self, *args, **options):
        for item in _concept.objects.all():
            if item.workgroup is not None:
                item.stewardship_organisation = item.workgroup.stewardship_organisation
                item.save()
