from django.core.management.base import BaseCommand
from django.apps import apps

from aristotle_mdr.utils.cache import recache_types


class Command(BaseCommand):
    args = ''
    help = 'Recaches types for concepts'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--id",
            default=None,
        )

    def handle(self, *args, **options):
        print('Updating search for object...')

        from aristotle_mdr.models import _concept
        instance = _concept.objects.get(pk=options['id']).item
        sender = instance.__class__
        # Pass to haystack signal processor
        processor = apps.get_app_config('haystack').signal_processor
        processor.handle_save(sender, instance)
