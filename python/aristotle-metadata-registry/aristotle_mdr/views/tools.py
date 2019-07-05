from django.views.generic import (
    TemplateView, ListView, View
)
from aristotle_mdr import models as MDR
from aristotle_mdr.views.utils import SimpleItemGet, paginate_sort_opts
from aristotle_mdr.utils import is_active_extension


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
            # If the URL query arg is set, filter on the selected one
            return self.kwargs['relation']
        else:
            # No URL query arg set, return the first one
            if not item.relational_attributes.keys():
                return None
            return list(item.relational_attributes.keys())[0]

    def get_queryset(self):
        item = self.get_item(self.request.user).item

        filtering_relation = self.get_current_relation()
        if not filtering_relation:
            return []

        queryset = item.relational_attributes[filtering_relation]['qs']
        queryset = queryset.visible(self.request.user)

        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_sort(self):
        sort_by=self.request.GET.get('sort', "name_asc")
        if sort_by not in paginate_sort_opts.keys():
            sort_by="name_asc"
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


class AristotleMetadataToolView(TemplateView):
    pass
