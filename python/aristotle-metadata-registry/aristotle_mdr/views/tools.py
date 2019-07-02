import logging
from django.views.generic import (
    TemplateView, ListView, View
)
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from aristotle_mdr import models as MDR
from aristotle_mdr.views.utils import SimpleItemGet, paginate_sort_opts
from aristotle_mdr.utils import is_active_extension
from aristotle_mdr.forms.forms import ReportingToolForm

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
        from aristotle_mdr.models import RegistrationAuthority, ObjectClass, DataElementConcept, DataElement, Status, ValueDomain, Property, _concept
        from django.db.models import Subquery, Q, Exists
        from django.contrib.contenttypes.models import ContentType

        registration_authority_id = form.cleaned_data['registration_authorities_select']
        data_type = form.cleaned_data['data_types_select']
        status = form.cleaned_data['statuses_select']

        ra = RegistrationAuthority.objects.get(id=registration_authority_id)

        statuses = Status.objects.current().filter(registrationAuthority=ra, state=status)
        logger.critical("THESE ARE THE ONES:")
        logger.critical(statuses.values('pk'))

        # DataElement
        if data_type == "0":

            non_standard_statuses = Status.objects.current().filter(registrationAuthority=ra).exclude(state=status)

            logger.critical("THESE ARE THE NON STANDARD STATUSES:")
            logger.critical(non_standard_statuses)

            non_standard_vd = ValueDomain.objects.filter(statuses__in=Subquery(non_standard_statuses.values('pk')))
            # non_standard_dec = DataElementConcept.objects.filter(statuses__in=Subquery(non_standard_statuses))
            # non_standard_oc = ObjectClass.objects.filter(statuses__in=Subquery(non_standard_statuses))
            # non_standard_prop = Property.objects.filter(statuses__in=Subquery(non_standard_statuses))

            logger.critical("THIS IS THE VD:")
            # logger.critical(non_standard_vd.values('pk'))

            logger.critical("THIS IS THE LIST")
            logger.critical(non_standard_vd)

            data_elements = DataElement.objects.filter(
                statuses__in=Subquery(statuses.values('pk')),

                # valueDomain_id__in=non_standard_vd,
                # dataElementConcept__pk__in=Subquery(non_standard_dec.values('pk'))

                valueDomain__statuses__in=Subquery(non_standard_statuses.values('pk')),
                dataElementConcept__statuses__in=Subquery(non_standard_statuses.values('pk')),
                dataElementConcept__objectClass__statuses__in=Subquery(non_standard_statuses.values('id')),
                dataElementConcept__property__statuses__in=Subquery(non_standard_statuses.values('pk')),
            ).order_by('name')[:50]


            # THIS IS NOT WORKING:

            # data_elements_standard_q = Q(statuses__in=Subquery(statuses.values('pk')))
            # value_domains_non_standard_q = Q(valueDomain__statuses__in=Subquery(non_standard_statuses.values('pk')))
            # dec_non_standard_q = Q(dataElementConcept__statuses__in=Subquery(non_standard_statuses.values('pk')))
            # dec_oc_non_standard_q = Q(dataElementConcept__objectClass__statuses__in=Subquery(non_standard_statuses.values('id')))
            # dec_p_non_standard_q = Q(dataElementConcept__property__statuses__in=Subquery(non_standard_statuses.values('pk')))
            #
            # data_elements = Q(
            #     data_elements_standard_q & Q(
            #         value_domains_non_standard_q |
            #         dec_non_standard_q |
            #         dec_oc_non_standard_q |
            #         dec_p_non_standard_q
            #     )
            # )
            #
            # data_elements = DataElement.objects.filter(data_elements)

            # data_elements = DataElement.objects.filter(
            #     Q(statuses__in=Subquery(statuses.values('pk'))) &
            #     Q(valueDomain__statuses__in=Subquery(non_standard_statuses.values('pk'))) &
            #     Q(dataElementConcept__statuses__in=Subquery(non_standard_statuses.values('pk'))) &
            #     # Q(dataElementConcept__objectClass__statuses__in=Subquery(non_standard_statuses.values('id'))) &
            #     Q(dataElementConcept__property__statuses__in=Subquery(non_standard_statuses.values('pk')))
            # )

            logger.critical("THIS IS THE RESULT:")
            # logger.critical(data_elements)
            logger.critical(data_elements)

            # data_elements = DataElement.objects.filter(statuses__in=Subquery(statuses.values('pk')))

        # DataElementConcept
        else:
            data_elements = DataElementConcept.objects.filter(statuses__in=Subquery(statuses.values('pk'))).order_by('name')

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





