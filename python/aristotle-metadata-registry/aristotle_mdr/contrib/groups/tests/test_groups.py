from django.test import TestCase
from aristotle_mdr.models import StewardOrganisation
import aristotle_mdr.tests.utils as utils
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache

import logging
logger = logging.getLogger(__name__)


class GroupsBulkActions(utils.AristotleTestUtils, TestCase):
    def setUp(self):
        super().setUp()

        cache.clear()

    def test_anonymous_users_dont_have_any_permission_for_groups(self):
        self.anonymous_user = AnonymousUser()
        self.abstract_group = StewardOrganisation.objects.create(name="Test Steward Organisation")
        for perm in self.abstract_group.role_permissions.keys():
            self.assertEqual(self.abstract_group.user_has_permission(self.anonymous_user, perm), False)

