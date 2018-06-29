from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

from autoslug import AutoSlugField


class AbstractMembershipBase(ModelBase):
    base_roles = Choices(
        ('owner', _('Owner')),
    )
    
    owner_role = "owner"
    roles = None
    extra_roles = None
    group_class = None
    group_kwargs = {}

    def __new__(cls, name, bases, attrs):  # noqa
        clsobj = super().__new__(cls, name, bases, attrs)

        try:
            field = clsobj._meta.get_field("role")
            if clsobj.roles:
                field.choices = clsobj.roles
            if clsobj.extra_roles:
                field.choices = clsobj.base_roles + clsobj.extra_roles
        except FieldDoesNotExist:
            clsobj.add_to_class(
                "role",
                models.CharField(
                    # choices=clsobj.roles,
                    max_length=128,
                    help_text=_('Role within this group')
                )
            )

        if clsobj.group_class is not None:
            clsobj.add_to_class(
                "group",
                models.ForeignKey(
                    clsobj.group_class,
                    related_name="members",
                    **clsobj.group_kwargs,
                )
            )

        return clsobj

class AbstractMembership(models.Model, metaclass=AbstractMembershipBase):
    class Meta:
        abstract = True
        unique_together = ("user", "group", "role")

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    roles = Choices(
        ('owner', _('Owner')),
    )

class AbstractGroupQuerySet(models.QuerySet):
    def group_list_for_user(self, user):
        return self.filter(members__user=user).distinct()

    def user_has_role(self, user, role):
        return self.filter(members__user=user, members__role=role).distinct()


class AbstractGroup(models.Model):
    objects = AbstractGroupQuerySet.as_manager()
    role_permissions = {
        "edit_group": [AbstractMembership.roles.owner],
        "edit_members": [AbstractMembership.roles.owner],
    }

    class Meta:
        abstract = True

    slug = AutoSlugField(populate_from='name', editable=True, always_update=False)
    name = models.TextField(
        help_text=_("The primary name used for human identification purposes.")
    )
    
    def __str__(self):
        return self.name

    @classmethod
    def member_list(cls, user):
        """
        Returns a list of groups that have the given user as a member
        """
        return cls.objects.filter(members__user=user).distinct()

    @property
    def roles(self):
        return self.members.model.roles

    def is_owner(self, user):
        """
        Returns true if the user has the specified role
        """
        return self.members.filter(user=user).exists()

    def is_member(self, user):
        """
        Returns true if the user has the specified role
        """
        return self.members.filter(user=user).exists()

    def has_role(self, role, user):
        """
        Returns true if the user has the specified role
        If role is a list, returns true if the user has any of the given roles
        """
        if type(role) is list:
            return self.members.filter(user=user, role__in=role).exists()
        return self.members.filter(user=user, role=role).exists()

    def grant_role(self, role, user):
        """
        Returns true if the user has the specified role
        """
        role, created = self.members.model.objects.get_or_create(group=self, user=user, role=role)
        
        return created 

    def revoke_role(self, role, user):
        """
        Remove given role for the user
        If role is a list, removes all of the given roles for the user
        Returns number of roles deleted
        """
        if type(role) is list:
            return self.members.filter(user=user, role__in=role).delete()
        return self.members.filter(user=user, role=role).delete()

    def revoke_membership(self, user):
        """
        Removes all roles.
        Returns number of roles deleted
        """
        deleted = self.members.filter(user=user).delete()
        return deleted 

    # def roles_for_user(self, user):
    #     """
    #     Removes all roles.
    #     Returns number of roles deleted
    #     """
    #     deleted = self.members.filter(user=user).delete()
    #     return deleted 

