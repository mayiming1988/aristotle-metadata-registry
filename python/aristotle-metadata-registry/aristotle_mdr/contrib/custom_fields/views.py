from typing import Iterable, List, Dict

from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import FormView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.contenttypes.models import ContentType

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.contrib.generic.views import VueFormView
from aristotle_mdr.contrib.generic.views import BootTableListView, CancelUrlMixin
from aristotle_mdr.contrib.custom_fields import models
from aristotle_mdr.contrib.slots.models import Slot

from aristotle_mdr.contrib.custom_fields.forms import CustomFieldForm, CustomFieldDeleteForm
from aristotle_mdr_api.v4.custom_fields.serializers import CustomFieldSerializer
from aristotle_mdr.utils.utils import get_concept_name_to_content_type, get_content_type_to_concept_name

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


class CustomFieldListCreateView(IsSuperUserMixin, ListView):
    template_name = 'aristotle_mdr/custom_fields/list_create.html'

    def get_queryset(self):
        metadata_types = {'all': 'All'}
        metadata_types.update(get_content_type_to_concept_name())

        return list(metadata_types.items())


class CustomFieldEditCreateView(IsSuperUserMixin, VueFormView):
    """ View to edit the values for all custom fields """
    template_name = 'aristotle_mdr/custom_fields/multiedit.html'
    form_class = CustomFieldForm
    non_write_fields = ['hr_type', 'hr_visibility']

    def get_custom_fields(self) -> Iterable[models.CustomField]:
        content_type_mapping = get_concept_name_to_content_type()

        metadata_type = self.kwargs['metadata_type']

        if metadata_type in content_type_mapping:
            content_type = content_type_mapping[metadata_type]
            return models.CustomField.objects.filter(allowed_model=content_type)
        elif metadata_type == 'all':
            return models.CustomField.objects.filter(allowed_model=None)
        else:
            raise Http404

    def get_vue_initial(self) -> List[Dict[str, str]]:
        fields = self.get_custom_fields()
        serializer = CustomFieldSerializer(fields, many=True)

        return serializer.data

    def get_allowed_models(self):
        allowed_models: Dict = {}
        # We don't need to do any form of permission checking because this is a super user only view
        for allowed_model in ContentType.objects.all():
            allowed_models[allowed_model.pk] = allowed_model.name.title()

        return allowed_models

    def get_name_of_edited_model(self, metadata_type):
        mapping = get_content_type_to_concept_name()
        if metadata_type in mapping:
            return mapping[metadata_type]
        return ''

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context['edited_model'] = self.get_name_of_edited_model(self.kwargs['metadata_type'])

        context['vue_allowed_models'] = json.dumps(self.get_allowed_models())
        return context


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
