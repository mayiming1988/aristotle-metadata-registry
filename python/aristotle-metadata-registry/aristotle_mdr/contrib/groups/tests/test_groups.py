from django.test import TestCase
from aristotle_mdr.models import StewardOrganisation
import aristotle_mdr.tests.utils as utils
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

from django.contrib.auth import get_user_model
from aristotle_mdr.utils import setup_aristotle_test_environment

from aristotle_mdr.contrib.groups.base import (
    AbstractMembership,
    AbstractGroup
)
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices

import logging
logger = logging.getLogger(__name__)

User = get_user_model()
setup_aristotle_test_environment()


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


class GroupsBulkActions(utils.AristotleTestUtils, TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_anonymous_users_dont_have_any_permission_for_groups(self):
        self.anonymous_user = AnonymousUser()
        self.abstract_group = StewardOrganisation.objects.create(name="Test Steward Organisation")
        for perm in self.abstract_group.role_permissions.keys():
            self.assertEqual(self.abstract_group.user_has_permission(self.anonymous_user, perm), False)

class GroupTestCase(TestCase):

    def test_group_state_choices(self):
        state_field = FakeGroup._meta.get_field('state')
        self.assertEqual(len(state_field.choices), 2)

    def test_membership_role_choices(self):
        role_field = FakeMembership._meta.get_field('role')
        self.assertEqual(len(role_field.choices), 3)
