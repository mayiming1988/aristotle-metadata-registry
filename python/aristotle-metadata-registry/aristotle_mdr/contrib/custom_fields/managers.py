from django.db.models import Manager


class CustomValueManager(Manager):

    def get_for_item(self, concept):
        qs = self.get_queryset().filter(
            concept=concept
        ).select_related('field')
        return qs
