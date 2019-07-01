from django.db.models import Manager
from django.db.models.query import QuerySet

from aristotle_mdr.constants import visibility_permission_choices as permission_choices


class SimplePermsQueryset(QuerySet):

    perm_field_name = 'permission'

    @property
    def perm_field_in(self):
        return self.perm_field_name + '__in'

    def visible(self, user, workgroup=None):
        perms = [permission_choices.public]
        if user is not None and user.is_authenticated:
            perms.append(permission_choices.auth)
            if user.is_superuser:
                return self
            elif workgroup in user.profile.workgroups:
                perms.append(permission_choices.workgroup)
        return self.filter(**{
            self.perm_field_in: perms
        })


class SlotsManager(Manager):

    def get_queryset(self):
        return SimplePermsQueryset(self.model, using=self._db)

    def get_item_allowed(self, concept, user):
        return self.get_queryset().filter(concept=concept).visible(user, concept.workgroup)
