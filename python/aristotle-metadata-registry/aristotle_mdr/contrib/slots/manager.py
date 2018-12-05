from django.db.models import Manager
from django.db.models.query import QuerySet
from aristotle_mdr.contrib.slots.choices import permission_choices as perms


class SlotsQueryset(QuerySet):

    def visible(self, user, workgroup=None):
        if user.is_authenticated:
            if workgroup in user.profile.workgroups:
                # return all slots
                return self
            else:
                # Return public and auth only slots
                return self.filter(permission__in=[perms.public, perms.auth])
        else:
            # Only return public slots
            return self.filter(permission=perms.public)


class SlotsManager(Manager):

    def get_queryset(self):
        return SlotsQueryset(self.model, using=self._db)

    def get_item_allowed(self, concept, user):
        return self.get_queryset().filter(concept=concept).visible(user, concept.workgroup)
