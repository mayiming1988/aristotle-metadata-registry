from django.db.models import Manager, Q
from aristotle_mdr.contrib.slots.manager import SimplePermsQueryset
from django.contrib.contenttypes.models import ContentType


class CustomFieldQueryset(SimplePermsQueryset):
    perm_field_name = 'visibility'


class CustomValueManager(Manager):

    def get_for_item(self, concept):
        qs = self.get_queryset().filter(
            concept=concept,
        ).select_related('field')
        return qs

    def get_allowed_for_item(self, concept, fields):
        """
        Return the values for a list of fields
        Used with get_allowed_fields
        """
        qs = self.get_queryset().filter(
            concept=concept,
            field__in=fields
        ).select_related('field')
        return qs


class CustomFieldManager(Manager):

    def get_queryset(self):
        return CustomFieldQueryset(self.model, using=self._db)

    def get_allowed_fields(self, concept, user):
        """Return the fields viewable on an item by a user"""
        return self.get_queryset().visible(user, concept.workgroup)

    def get_for_model(self, model):
        """Return the fields for a given model"""
        ct = ContentType.objects.get_for_model(model)
        fil = Q(allowed_model__isnull=True) | Q(allowed_model=ct)
        return self.get_queryset().filter(fil)
