from typing import Iterable, List, Dict
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.contenttypes.models import ContentType

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.contrib.generic.views import VueFormView
from aristotle_mdr.contrib.generic.views import BootTableListView, CancelUrlMixin
from aristotle_mdr.contrib.custom_fields import models
from aristotle_mdr.contrib.custom_fields.forms import CustomFieldForm, CustomFieldDeleteForm
from aristotle_mdr_api.v4.custom_fields.serializers import CustomFieldSerializer
from aristotle_mdr.contrib.slots.models import Slot

import json


class CustomFieldListView(IsSuperUserMixin, BootTableListView):
    template_name='aristotle_mdr/custom_fields/list.html'
    model=models.CustomField
    paginate_by=20
    model_name='Custom Field'
    headers = ['Name', 'Type', 'Help Text', 'Model', 'Visibility']
    attrs = ['name', 'hr_type', 'help_text', 'allowed_model', 'hr_visibility']
    blank_value = {
        'allowed_model': 'All'
    }

    delete_url_name = 'aristotle_custom_fields:delete'


class CustomFieldMultiEditView(IsSuperUserMixin, VueFormView):
    """ View to edit the values for all custom fields """
    template_name='aristotle_mdr/custom_fields/multiedit.html'
    form_class=CustomFieldForm
    non_write_fields = ['hr_type', 'hr_visibility']

    def get_custom_fields(self) -> Iterable[models.CustomField]:
        return models.CustomField.objects.all()

    def get_vue_initial(self) -> List[Dict[str, str]]:
        fields = self.get_custom_fields()
        serializer = CustomFieldSerializer(fields, many=True)

        return serializer.data

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()

        context['vue_allowed_models'] = json.dumps(self.get_allowed_models())
        return context

    def get_allowed_models(self):
        allowed_models: Dict = {}
        # We don't need to do any form of permission checking because this is a super user only view
        for allowed_model in ContentType.objects.all():
            allowed_models[allowed_model.pk] = allowed_model.name.title()

        return allowed_models


class CustomFieldDeleteView(IsSuperUserMixin, CancelUrlMixin, SingleObjectMixin, FormView):
    model=models.CustomField
    form_class=CustomFieldDeleteForm
    template_name='aristotle_mdr/custom_fields/delete.html'
    cancel_url_name='aristotle_custom_fields:list'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def delete(self):
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def migrate(self):
        new_slots = []
        existing_values = models.CustomValue.objects.filter(field=self.object)
        for value in existing_values:
            vslot = Slot(
                name=self.object.name[:256],
                type=self.object.hr_type,
                concept_id=value.concept_id,
                permission=self.object.visibility,
                value=value.content
            )
            new_slots.append(vslot)

        Slot.objects.bulk_create(new_slots)
        return self.delete()

    def form_valid(self, form):
        method = form.cleaned_data['method']

        if method == 'delete':
            return self.delete()
        elif method == 'migrate':
            return self.migrate()

    def get_success_url(self) -> str:
        return reverse('aristotle_custom_fields:list')
