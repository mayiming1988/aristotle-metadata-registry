from django.core.management.base import BaseCommand

from aristotle_mdr.utils.cache import recache_types


class Command(BaseCommand):
    args = ''
    help = 'Recaches types for concepts'

    def handle(self, *args, **kwargs):
        print('Updating caches...')
        updated = recache_types()
        print('Updated type for the following models:')
        for label in updated:
            print('\t{label}'.format(label=label))
