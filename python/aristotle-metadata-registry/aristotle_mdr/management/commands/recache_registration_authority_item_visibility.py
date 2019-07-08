from django.core.management.base import BaseCommand, CommandError
from aristotle_mdr.models import RegistrationAuthority, _concept


class Command(BaseCommand):
    args = '<workgroup_id workgroup_id ...>'
    help = 'Recomputes and caches the public and locked statuses for the given workgroup(s). This is useful if the registration authorities associated with a workgroup change.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--ra",
            nargs='*',
            default=None,
        )

    def handle(self, *args, **options):
        from haystack import connections
        if options['ra'] is None:
            ras = RegistrationAuthority.objects.all().values_list('id', flat=True)
        else:
            ras = options['ra']

        for item in _concept.objects.filter(statuses__registrationAuthority__in=ras):
            # self.stdout.write(' Updating item (id:%s)' % (item.id))
            item.recache_states()
            connections['default'].get_unified_index().get_index(item.item.__class__).update_object(item.item)
            self.stdout.write(' Updated! item (id:%s)' % (item.id))

        self.stdout.write('Successfully updated items!')
