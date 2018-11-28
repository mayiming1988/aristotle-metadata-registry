from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.contrib.custom_fields import models


class CreateCustomFieldView(IsSuperUserMixin, CreateView):
    model=models.CustomField
    fields='__all__'
    template_name='aristotle_mdr/custom_fields/create_field.html'

    def get_success_url(self):
        return reverse('aristotle_mdr:userAdminTools')
