from django.db.models import Manager
from django.db.models.query import QuerySet
from aristotle_mdr.contrib.slots.choices import permission_choices as perms


class SimplePermsQueryset(QuerySet):

    perm_field_name = 'permission'

    @property
    def perm_field_in(self):
        return self.perm_field_name + '__in'

    def visible(self, user, workgroup=None):
        if user.is_authenticated:
            if workgroup in user.profile.workgroups or user.is_superuser:
                # return all slots
                return self
            else:
                # Return public and auth only slots
                kwargs = {
                    self.perm_field_in: [perms.public, perms.auth]
                }
                return self.filter(**kwargs)
        else:
            # Only return public slots
            kwargs = {
                self.perm_field_name: perms.public
            }
            return self.filter(**kwargs)


class SlotsManager(Manager):

    def get_queryset(self):
        return SimplePermsQueryset(self.model, using=self._db)

    def get_item_allowed(self, concept, user):
        return self.get_queryset().filter(concept=concept).visible(user, concept.workgroup)
