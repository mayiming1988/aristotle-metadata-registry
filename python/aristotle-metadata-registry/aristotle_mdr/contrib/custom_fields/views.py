from typing import Iterable, List, Dict
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.views.utils import VueFormView
from aristotle_mdr.views.generic import BootTableListView, CancelUrlMixin
from aristotle_mdr.contrib.custom_fields import models
from aristotle_mdr.contrib.custom_fields.forms import CustomFieldForm
from aristotle_mdr_api.v4.custom_fields.serializers import CustomFieldSerializer

import json


class CustomFieldCreateView(IsSuperUserMixin, CancelUrlMixin, CreateView):
    model=models.CustomField
    fields='__all__'
    template_name='aristotle_mdr/custom_fields/field_form.html'
    cancel_url_name='aristotle_custom_fields:list'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['heading'] = 'Create Custom Field'
        context['submit_text'] = 'Create'
        return context

    def get_success_url(self):
        return reverse('aristotle_custom_fields:list')


class CustomFieldUpdateView(IsSuperUserMixin, CancelUrlMixin, UpdateView):
    model=models.CustomField
    fields='__all__'
    template_name='aristotle_mdr/custom_fields/field_form.html'
    cancel_url_name='aristotle_custom_fields:list'

    def get_success_url(self):
        return reverse('aristotle_custom_fields:list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['heading'] = 'Update Custom Field'
        context['submit_text'] = 'Update'
        return context


class CustomFieldDeleteView(IsSuperUserMixin, CancelUrlMixin, DeleteView):
    model=models.CustomField
    template_name='aristotle_mdr/custom_fields/delete.html'
    cancel_url_name='aristotle_custom_fields:list'

    def get_success_url(self) -> str:
        return reverse('aristotle_custom_fields:list')


class CustomFieldListView(IsSuperUserMixin, BootTableListView):
    template_name='aristotle_mdr/custom_fields/list.html'
    model=models.CustomField
    paginate_by=20
    model_name='Custom Field'
    headers = ['Name', 'Type', 'Help Text']
    attrs = ['name', 'hr_type', 'help_text']


class CustomFieldMultiEditView(VueFormView):
    template_name='aristotle_mdr/custom_fields/multiedit.html'
    form_class=CustomFieldForm

    def get_custom_fields(self) -> Iterable[models.CustomField]:
        return models.CustomField.objects.all()

    def get_vue_initial(self) -> List[Dict[str, str]]:
        fields = self.get_custom_fields()
        serializer = CustomFieldSerializer(fields, many=True)
        return serializer.data
