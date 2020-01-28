import logging

import aristotle_mdr.tests.utils as utils
from aristotle_mdr.contrib.groups.base import (
    AbstractMembership,
    AbstractGroup
)
from aristotle_mdr.models import StewardOrganisation
from model_utils import Choices

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test import TestCase, tag
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from django.core import mail
from unittest import skip

logger = logging.getLogger(__name__)

User = get_user_model()


class BaseGroupsTestCase(utils.AristotleTestUtils):
    def setUp(self):
        super().setUp()
        cache.clear()

        self.steward_org = StewardOrganisation.objects.create(
            name="Test Stewardship Organisation",
            description="Test test test",
            state=StewardOrganisation.states.active,
        )

        self.steward_org_slug = self.steward_org.slug

        self.user_in_steward_org = User.objects.create(
            email='steve@aristotle.example.com',
            short_name='steve'
        )
        self.steward_org.grant_role(
            role=StewardOrganisation.roles.member,
            user=self.user_in_steward_org
        )

    def get_url_from_email(self, email_content):
        start = email_content.find('http://')
        end = email_content.find('\n', start)
        accept_url = email_content[start:end]

        return accept_url[7:]


@tag('invite_stewardship_user')
@skip("Skipped until we have time to fix inviting")
class InviteUserToStewardGroup(BaseGroupsTestCase, TestCase):
    def test_created_user_is_added_to_stewardship_org(self):
        self.login_superuser()

        url = reverse('aristotle_mdr:stewards:group:invite', args=[self.steward_org_slug])

        # Field is called emails
        # Create a new user
        response = self.client.post(
            url,
            {'email_list': 'test@example.com'},
        )
        self.assertEqual(response.status_code, 302)

        # Test that the user was created
        user = User.objects.get(email='test@example.com')

        # Test that the email was sent
        self.assertEqual(len(mail.outbox), 1)

        # Logout the superuser
        self.logout()

        # Get the email content from the user
        message = mail.outbox[0].body
        print(message)

        # Get the accept URL
        accept_url = self.get_url_from_email(message)
        accept_response = self.client.get(accept_url)

        self.assertEqual(accept_response.status_code, 200)

        accept_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'short_name': 'Test',
            'password': 'verynice',
            'password_confirm': 'verynice'
        }

        response = self.client.post(accept_url, accept_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aristotle_mdr/friendly_login.html')
        self.assertTrue('welcome' in response.context.keys())

        new_user = get_user_model().objects.get(email='test@example.com')
        self.assertTrue(new_user.is_active)
        self.assertTrue(new_user.password)
        self.assertEqual(new_user.short_name, 'Test')
        self.assertEqual(new_user.full_name, 'Test User')

        # Check that the invited user is added
        self.assertTrue(self.steward_org.has_member(user))



class GroupsBulkActions(utils.AristotleTestUtils, TestCase):
    def setUp(self):
        super().setUp()
        cache.clear()

    def test_anonymous_users_dont_have_any_permission_for_groups(self):
        self.anonymous_user = AnonymousUser()
        self.abstract_group = StewardOrganisation.objects.create(name="Test Steward Organisation")
        for perm in self.abstract_group.role_permissions.keys():
            if perm is "view_group":
                # We have one anon permitted permission now
                continue
            self.assertEqual(self.abstract_group.user_has_permission(self.anonymous_user, perm), False)


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
