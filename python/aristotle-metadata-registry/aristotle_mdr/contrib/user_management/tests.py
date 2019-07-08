from django.urls import reverse
from django.test import TestCase

from aristotle_mdr.tests import utils


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

    def test_view_all_perms(self):
        from aristotle_mdr import models
        from django.contrib.auth import get_user_model

        User = get_user_model()

        peeping_tom = User.objects.create(
            email="tom@aristotle.example.com",
            short_name="Tom"
        )
        hidden_oc = models.ObjectClass.objects.create(
            name="Hidden content",
            stewardship_organisation=None,
            workgroup=None,
            submitter=None,
        )
        self.assertTrue(hidden_oc not in models.ObjectClass.objects.visible(peeping_tom))
        peeping_tom.perm_view_all_metadata = True
        peeping_tom.save()
        self.assertTrue(hidden_oc in models.ObjectClass.objects.visible(peeping_tom))

        peeping_tom.perm_view_all_metadata = False
        peeping_tom.save()
        self.assertTrue(hidden_oc not in models.ObjectClass.objects.visible(peeping_tom))
