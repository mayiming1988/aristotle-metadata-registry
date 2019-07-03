import logging
from django.views.generic import (
    TemplateView, ListView, View
)
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from aristotle_mdr import models as MDR
from aristotle_mdr.views.utils import SimpleItemGet, paginate_sort_opts, SortedListView
from aristotle_mdr.utils import is_active_extension
from aristotle_mdr.forms.forms import ReportingToolForm
from aristotle_mdr.models import RegistrationAuthority, ObjectClass, DataElementConcept, DataElement, Status, ValueDomain, Property
from django.db.models import Q

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)


class ItemGraphView(SimpleItemGet, TemplateView):
    model = MDR._concept
    template_name = "aristotle_mdr/graphs/item_graphs.html"
    pk_url_kwarg = 'iid'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['activetab'] = 'graphs'
        context['hide_item_actions'] = True
        context['item'] = self.item.item
        context['links_active'] = is_active_extension('aristotle_mdr_links')
        return context


class ConceptRelatedListView(SimpleItemGet, ListView):
    template_name = "aristotle_mdr/concepts/tools/related.html"

    def get_paginate_by(self, queryset):
        return self.request.GET.get('pp', 20)

    def get_current_relation(self):
        item = self.get_item(self.request.user).item
        if self.kwargs['relation'] in item.relational_attributes.keys():
            return self.kwargs['relation']
        else:
            return list(item.relational_attributes.keys())[0]

    def get_queryset(self):
        item = self.get_item(self.request.user).item
        queryset = item.relational_attributes[self.get_current_relation()]['qs']
        queryset = queryset.visible(self.request.user)

        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_sort(self):
        sort_by = self.request.GET.get('sort', "name_asc")
        if sort_by not in paginate_sort_opts.keys():
            sort_by = "name_asc"
        return sort_by

    def get_ordering(self):
        return paginate_sort_opts.get(self.get_sort())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['activetab'] = 'related'
        context['current_relation'] = self.get_current_relation()
        context['relational_attributes'] = self.item.item.relational_attributes
        context['hide_item_actions'] = True
        context['item'] = self.item.item
        context['sort'] = self.get_sort()
        return context


class AristotleMetadataToolView(TemplateView, FormView):
    template_name = "aristotle_mdr/concepts/tools/reporting_tool.html"
    form_class = ReportingToolForm
    paginate_by = 20

    def form_invalid(self, form):
        # Do something if the form is invalid.
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET
            })
        return kwargs

    def get_success_url(self):
        return reverse("aristotle:reportingTool")

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def form_valid(self, form):

        registration_authority_id = form.cleaned_data['ra']
        status = form.cleaned_data['status']

        ra = RegistrationAuthority.objects.get(id=registration_authority_id)

        non_standard_statuses = Status.objects.current().filter(registrationAuthority=ra).exclude(state=status)

        standard_statuses = Status.objects.current().filter(
            registrationAuthority=registration_authority_id,
            state=status
        )

        data_elements = DataElement.objects.filter(
            statuses__in=standard_statuses
        )

        value_domains_query = ValueDomain.objects.filter(
            dataelement__in=data_elements,
            statuses__in=non_standard_statuses
        )

        data_elements_concepts_query = DataElementConcept.objects.filter(
            dataelement__in=data_elements,
        )

        object_class_query = ObjectClass.objects.filter(
            dataelementconcept__in=data_elements_concepts_query,
            statuses__in=non_standard_statuses
        )

        properties_query = Property.objects.filter(
            dataelementconcept__in=data_elements_concepts_query,
            statuses__in=non_standard_statuses
        )

        # Get all the DEC with non standard statuses or components with non standard statuses
        data_elements_concepts_query = data_elements_concepts_query.filter(
            Q(statuses__in=non_standard_statuses) |
            Q(property__in=properties_query) |
            Q(objectClass__in=object_class_query)
        )

        # Return all the filtered Data Elements with non standard DEC or non standard ValueDomains
        data_elements = data_elements.filter(
            Q(dataElementConcept__in=data_elements_concepts_query) |
            Q(valueDomain__in=value_domains_query)
        )

        context = {
            'form': form,
            'data_elements': data_elements
        }
        return self.render_to_response(self.get_context_data(**context))

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if self.form_class.is_valid(form):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def fetch_dataelements(self, ra, status):
        """
        Fetch data elements with a specific status where the components
        have a different status
        :param ra: Registration Authority.
        :param status: Status corresponding to the Data Element, but not corresponding to subcomponents.
        :return:
        """

        non_standard_statuses = Status.objects.current().filter(registrationAuthority=ra).exclude(state=status)

        standard_statuses = Status.objects.current().filter(
            registrationAuthority=ra,
            state=status
        )

        data_elements = DataElement.objects.filter(
            statuses__in=standard_statuses
        )

        value_domains_query = ValueDomain.objects.filter(
            dataelement__in=data_elements,
            statuses__in=non_standard_statuses
        )

        data_elements_concepts_query = DataElementConcept.objects.filter(
            dataelement__in=data_elements,
        )

        object_class_query = ObjectClass.objects.filter(
            dataelementconcept__in=data_elements_concepts_query,
            statuses__in=non_standard_statuses
        )

        properties_query = Property.objects.filter(
            dataelementconcept__in=data_elements_concepts_query,
            statuses__in=non_standard_statuses
        )

        # Get all the DEC with non standard statuses or components with non standard statuses
        data_elements_concepts_query = data_elements_concepts_query.filter(
            Q(statuses__in=non_standard_statuses) |
            Q(property__in=properties_query) |
            Q(objectClass__in=object_class_query)
        )

        # Return all the filtered Data Elements with non standard DEC or non standard ValueDomains
        data_elements = data_elements.filter(
            Q(dataElementConcept__in=data_elements_concepts_query) |
            Q(valueDomain__in=value_domains_query)
        )
        return data_elements

    def fetch_components_for_dataelement(self, dataelement_list_ids):
        """
        Given a list of Data Element ids, provide their corresponding subcomponents
        (ValueDomain, DEC's Object Class, and DEC's Property).
        The purpose is to use select_related on the given list to reduce Database hits from template as much as possible.
        :param dataelement_list_ids: list with the Data Element ids
        :return: Queryset with Data Element objects and their corresponding fetched subcomponents.
        """

        related_objects = [
            'valueDomain',
            'dataElementConcept__objectClass',
            'dataElementConcept__property',
        ]

        data_elements = DataElement.objects.filter(id__in=dataelement_list_ids)

        return data_elements.select_related(*related_objects)

