from django.urls import reverse
from django.test import TestCase

from aristotle_mdr.tests import utils
from aristotle_mdr.utils import setup_aristotle_test_environment

setup_aristotle_test_environment()


class TestUserpages(utils.LoggedInViewPages, TestCase):

    def test_superuser_can_view(self):
        self.login_superuser()
        response = self.client.get(reverse('aristotle-user:registry_user_list',))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle-user:update_another_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle-user:deactivate_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle-user:reactivate_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('aristotle-user:update_another_user_site_perms', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 200)

    def test_registrar_cannot_view(self):
        self.login_registrar()
        response = self.client.get(reverse('aristotle-user:registry_user_list',))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:update_another_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:deactivate_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:reactivate_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:update_another_user_site_perms', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)

    def test_editor_cannot_view(self):
        self.login_registrar()
        response = self.client.get(reverse('aristotle-user:registry_user_list',))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:update_another_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:deactivate_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:reactivate_user', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('aristotle-user:update_another_user_site_perms', args=[self.editor.pk]))
        self.assertEqual(response.status_code, 403)
