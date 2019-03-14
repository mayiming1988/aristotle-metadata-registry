from django.urls import reverse
from django.test import TestCase

from aristotle_mdr.contrib.groups.base import (
    AbstractMembership,
    AbstractGroup
)

from django.utils.translation import ugettext_lazy as _
from model_utils import Choices


class FakeGroup(AbstractGroup):

    roles = Choices(
        ('best', _('Best')),
        ('ok', _('Ok')),
        ('bad', _('Bad')),
    )
    owner_roles = [roles.best]
    new_member_role = roles.bad

    states = Choices(
        ('on', _('On')),
        ('off', _('Off & Visible')),
    )

    active_states = [
        states.on,
    ]
    visible_states = [
        states.off
    ]

    role_permissions = {
        'can_do_a_safe_thing': [roles.ok, roles.bad],
        'can_do_an_unsafe_thing': [roles.best]
    }


class FakeMembership(AbstractMembership):
    group_class = FakeGroup


class GroupTestCase(TestCase):

    def test_group_state_choices(self):
        state_field = FakeGroup._meta.get_field('state')
        self.assertEqual(len(state_field.choices), 2)

    def test_membership_role_choices(self):
        role_field = FakeMembership._meta.get_field('role')
        self.assertEqual(len(role_field.choices), 3)
