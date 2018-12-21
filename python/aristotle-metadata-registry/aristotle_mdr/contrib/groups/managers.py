from django.db import models
from django.db.models import Q


class AbstractGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(state__in=self.model.active_states)

    def group_list_for_user(self, user):
        return self.filter(members__user=user).distinct()

    def user_has_role(self, user, role):
        return self.filter(members__user=user, members__role=role).distinct()
