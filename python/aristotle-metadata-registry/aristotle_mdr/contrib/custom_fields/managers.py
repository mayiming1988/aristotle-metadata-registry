from django.db.models import Manager
from aristotle_mdr.contrib.slots.manager import SimplePermsQueryset


class CustomValueQueryset(SimplePermsQueryset):

    perm_field_name = 'visibility'


class CustomValueManager(Manager):

    def get_for_item(self, concept):
        qs = self.get_queryset().filter(
            concept=concept,
        ).select_related('field')
        return qs

    def get_allowed_for_item(self, concept, fields):
        qs = self.get_queryset().filter(
            concept=concept,
            field__in=fields
        ).select_related('field')
        return qs


class CustomFieldManager(Manager):

    def get_queryset(self):
        return CustomValueQueryset(self.model, using=self._db)

    def get_allowed_fields(self, concept, user):
        return self.get_queryset().visible(user, concept.workgroup)
