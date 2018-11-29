from django.urls import reverse
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.views.generic import BootTableListView, CancelUrlMixin
from aristotle_mdr.contrib.custom_fields import models


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

    def get_success_url(self):
        return reverse('aristotle_custom_fields:list')


class CustomFieldListView(IsSuperUserMixin, BootTableListView):
    model=models.CustomField
    paginate_by=20
    model_name='Custom Field'
    headers = ['Name', 'Type', 'Help Text']
    attrs = ['name', 'type', 'help_text']
    create_url_name='aristotle_custom_fields:create'
    update_url_name='aristotle_custom_fields:update'
    delete_url_name='aristotle_custom_fields:delete'
