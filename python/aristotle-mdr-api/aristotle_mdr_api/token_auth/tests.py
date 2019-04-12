from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import Http404
from django.views.generic import TemplateView

from aristotle_mdr_api.token_auth.mixins import TokenAuthMixin
from aristotle_mdr_api.token_auth.models import AristotleToken


class FakeTokenAuthView(TokenAuthMixin, TemplateView):
    template_name='aristotle_mdr/base.html'


class TokenAuthMixinTestCase(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'reggie',
            'rock'
        )
        self.token = AristotleToken.objects.create(
            name='Reggie\'s token',
            key='abcdef',
            user=self.user,
            permissions={'default': {'read': True, 'write': True}}
        )
        self.factory = RequestFactory()
        self.view = FakeTokenAuthView()

    def call_with_auth_header(self, auth_header):
        request = self.factory.get('/some/api')
        request.META['HTTP_AUTHORIZATION'] = auth_header
        self.view.request = request
        response = self.view.dispatch(request)
        return response

    def test_404_on_non_token_request(self):
        request = self.factory.get('/some/api')
        self.view.request = request
        response = self.view.dispatch(request)
        self.assertIsNone(self.view.token_user)

    def test_user_set_from_token(self):
        response = self.call_with_auth_header('Token abcdef')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.view.token_user, self.user)

    def test_non_existant_token(self):
        response = self.call_with_auth_header('Token www')
        self.assertEqual(response.status_code, 400)

    def test_no_read_perms(self):
        self.token.permissions = {'default': {'read': False}}
        self.token.save()
        response = self.call_with_auth_header('Token abcdef')
        self.assertEqual(response.status_code, 403)
