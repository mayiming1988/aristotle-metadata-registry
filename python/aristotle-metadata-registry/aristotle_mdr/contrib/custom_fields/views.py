from typing import Iterable, List, Dict

from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.generic import FormView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.contenttypes.models import ContentType

from aristotle_mdr.mixins import IsSuperUserMixin
from aristotle_mdr.contrib.generic.views import VueFormView
from aristotle_mdr.contrib.custom_fields import models
from aristotle_mdr.contrib.slots.models import Slot

from aristotle_mdr.contrib.custom_fields.forms import CustomFieldForm, CustomFieldDeleteForm
from aristotle_mdr_api.v4.custom_fields.serializers import CustomFieldSerializer
from aristotle_mdr.utils.utils import get_concept_name_to_content_type, get_content_type_to_concept_name

import json
import logging
logger = logging.getLogger(__name__)


class CustomFieldListView(IsSuperUserMixin, ListView):

    template_name = 'aristotle_mdr/custom_fields/list.html'
    model = models.CustomField
    paginate_by = 20
    model_name = 'Custom Field'
    table_headers = ['Name', 'Type', 'Help Text', 'Model', 'Visibility']
    model_attrs = ['name', 'hr_type', 'help_text', 'allowed_model', 'hr_visibility']
    model_blank_field_replacement = {
        'allowed_model': 'All',
    }

    delete_url_name = 'aristotle_custom_fields:delete'

    def dispatch(self, request, *args, **kwargs):
        self.foreign_key_extra_filtering_value = kwargs.get('content_type')
        return super().dispatch(request, *args, **kwargs)

    def get_listing(self, iterable) -> List[Dict]:
        listing = []
        for item in iterable:
            itemdict = {'attrs': [], 'pk': item.pk}
            for attr in self.model_attrs:
                val = getattr(item, attr)
                if not val and attr in self.model_blank_field_replacement:
                    val = self.model_blank_field_replacement[attr]
                itemdict['attrs'].append(val)
            listing.append(itemdict)

        return listing

    def get_queryset(self):
        my_ct = ContentType.objects.get(model=self.foreign_key_extra_filtering_value)
        queryset = models.CustomField.objects.filter(allowed_model=my_ct)
        return queryset

    def get_context_data(self, **kwargs) -> dict:

        context = super().get_context_data()

        if context['page_obj'] is not None:
            iterable = context['page_obj']
        else:
            iterable = context['object_list']

        final_list = self.get_listing(iterable)

        context.update({
            'list': final_list,
            'delete_url_name': self.delete_url_name,
        })
        return context


class CustomFieldListCreateView(IsSuperUserMixin, ListView):
    template_name = 'aristotle_mdr/custom_fields/list_create.html'

    def get_queryset(self):
        metadata_types = {'all': 'All'}
        metadata_types.update(get_content_type_to_concept_name())

        return list(sorted(metadata_types.items()))


class CustomFieldEditCreateView(IsSuperUserMixin, VueFormView):
    """
    View to edit the values for all custom fields
    """
    template_name = 'aristotle_mdr/custom_fields/multiedit.html'
    form_class = CustomFieldForm
    non_write_fields = ['hr_type', 'hr_visibility']

    def dispatch(self, request, *args, **kwargs):
        self.metadata_type = kwargs.get('metadata_type')
        return super().dispatch(request, args, kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        self.content_type = self.get_name_of_edited_model(self.metadata_type)
        context.update({
            'edited_model': self.content_type,
            'vue_allowed_models': json.dumps(self.get_allowed_models()),
            'vue_formset_add_button_message': "Add Custom Field for {}".format(self.content_type),
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(CustomFieldEditCreateView, self).get_form_kwargs()
        kwargs.update({
            'content_type': self.metadata_type
        })
        return kwargs

    def get_vue_initial(self) -> List[Dict[str, str]]:
        fields = self.get_custom_field_objects()
        serializer = CustomFieldSerializer(fields, many=True)
        return serializer.data

    def get_custom_field_objects(self) -> Iterable[models.CustomField]:
        """
        Get a Queryset of CustomField objects.
        :return: Queryset
        """
        content_type_mapping = get_concept_name_to_content_type()

        if self.metadata_type in content_type_mapping:
            content_type = content_type_mapping[self.metadata_type]
            return models.CustomField.objects.filter(allowed_model=content_type)
        elif self.metadata_type == 'all':
            return models.CustomField.objects.filter(allowed_model=None)
        else:
            raise Http404

    def get_allowed_models(self):
        allowed_models: Dict = {}
        # We don't need to do any form of permission checking because this is a super user only view.
        for allowed_model in ContentType.objects.all():
            allowed_models[allowed_model.pk] = allowed_model.name.title()

        return allowed_models

    def get_name_of_edited_model(self, metadata_type):
        mapping = get_content_type_to_concept_name()
        if metadata_type in mapping:
            return mapping[metadata_type]
        return 'All Models'


class CustomFieldDeleteView(IsSuperUserMixin, SingleObjectMixin, FormView):
    model = models.CustomField
    form_class = CustomFieldDeleteForm
    template_name = 'aristotle_mdr/custom_fields/delete.html'
    cancel_url_name = 'aristotle_custom_fields:edit'

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
        if self.object.allowed_model:
            return reverse('aristotle_custom_fields:list', args=[self.object.allowed_model.model])
        else:
            return reverse('aristotle_custom_fields:list', args=["all"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "cancel_url": reverse('aristotle_custom_fields:edit')
        })
        return context
