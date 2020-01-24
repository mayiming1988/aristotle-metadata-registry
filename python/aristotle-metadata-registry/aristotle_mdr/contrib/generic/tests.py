from django.urls import reverse
from django import forms
from django.test import TestCase, RequestFactory

from aristotle_mdr.tests import utils
from aristotle_mdr.contrib.generic.views import VueFormView

import json


class TestGenericPagesLoad(utils.LoggedInViewPages, TestCase):

    def test_anon_cant_use_generic(self):
        from extension_test.models import Questionnaire
        from aristotle_mdr.models import Workgroup

        wg = Workgroup.objects.create(name="Setup WG", stewardship_organisation=self.steward_org_1)
        q = Questionnaire.objects.create(name='test questionnaire', workgroup=wg)
        url = reverse('extension_test:questionnaire_add_question', kwargs={'iid': q.id})
        response = self.client.get(url)
        self.assertRedirects(response, reverse('friendly_login') + "?next=" + url)


class VueFormTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.view = VueFormView()

    def get_test_form(self):
        tchoices = [('a', 'apple'), ('b', 'bananna')]
        fields = {
            'name': forms.CharField(max_length=200, required=True, label='Name'),
            'description': forms.CharField(min_length=200, label='Description', initial='wow'),
            'fruit': forms.ChoiceField(choices=tchoices, initial='b')
        }
        return type('MyForm', (forms.Form,), fields)

    def setup_view(self):
        self.view.form_class = self.get_test_form()
        self.view.request = self.factory.get('/vueform/')

    def get_fields(self):
        self.setup_view()
        context = self.view.get_context_data()
        fields = json.loads(context['vue_fields'])
        return fields

    def test_tags_fields_and_initial_present(self):
        self.setup_view()
        context = self.view.get_context_data()
        self.assertTrue('vue_fields' in context)
        self.assertTrue('vue_initial' in context)
        fields = json.loads(context['vue_fields'])
        self.assertTrue('name' in fields)
        self.assertTrue('fruit' in fields)

    def test_tags_correct(self):
        fields = self.get_fields()
        self.assertEqual(fields['name']['tag'], 'textarea')
        self.assertEqual(fields['description']['tag'], 'textarea')
        self.assertEqual(fields['fruit']['tag'], 'select')

    def test_labels_correct(self):
        fields = self.get_fields()
        self.assertEqual(fields['name']['label'], 'Name')
        self.assertEqual(fields['description']['label'], 'Description')
        self.assertIsNone(fields['fruit']['label'])

    def test_options_correct(self):
        fields = self.get_fields()
        self.assertEqual(fields['name']['options'], [])
        self.assertEqual(fields['description']['options'], [])
        self.assertCountEqual(fields['fruit']['options'], [['a', 'Apple'], ['b', 'Bananna']])

    def test_rules_correct(self):
        fields = self.get_fields()
        self.assertCountEqual(fields['name']['rules'], {'required': True, 'max_length': 200})
        self.assertCountEqual(fields['description']['rules'], {'required': True, 'min_length': 200})
        self.assertCountEqual(fields['fruit']['rules'], {'required': False})

    def test_default_values_correct(self):
        fields = self.get_fields()
        self.assertEqual(fields['name']['default'], None)
        self.assertEqual(fields['description']['default'], 'wow')
        self.assertEqual(fields['fruit']['default'], 'b')

    def test_overwrite_initial(self):
        self.view.get_vue_initial = lambda: {'name': 'TheBest', 'fruit': 'a'}
        self.setup_view()
        context = self.view.get_context_data()
        self.assertEqual(json.loads(context['vue_initial']), {'name': 'TheBest', 'fruit': 'a'})

    def test_strip_fields(self):
        self.view.non_write_fields = ['fruit']
        self.view.get_vue_initial = lambda: {'name': 'TheBest', 'fruit': 'a'}
        self.setup_view()
        context = self.view.get_context_data()
        self.assertEqual(json.loads(context['vue_initial']), {'name': 'TheBest'})

    def test_post_not_permitted(self):
        self.view.form_class = self.get_test_form()
        request = self.factory.post('/vueform/')
        self.view.request = request
        response = self.view.dispatch(request)
        self.assertEqual(response.status_code, 405)
