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

    # def get(self, request, *args, **kwargs):
    #     item = self.get_item(request.user)
    #     self.item = item
    #     return super(ItemGraphView, self).get(request, *args, **kwargs)

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


from aristotle_mdr.forms import CompareConceptsForm
from aristotle_mdr.models import _concept
from .versions import ConceptVersionCompareBase
from reversion.models import Version

class MetadataComparison(ConceptVersionCompareBase, AristotleMetadataToolView):
    template_name = 'aristotle_mdr/actions/compare/compare_items_2.html'

    def get_form(self):
        data = self.request.GET
        user = self.request.user
        qs = _concept.objects.visible(user)
        return CompareConceptsForm(data, user=user, qs=qs)  # A form bound to the POST data

    def get_version_1_concept(self):
        form = self.get_form()
        if form.is_valid():
            # Get items from form
            return form.cleaned_data['item_a'].item
        return None

    def get_version_2_concept(self):
        form = self.get_form()
        if form.is_valid():
            # Get items from form
            return form.cleaned_data['item_b'].item
        return None

    def get_compare_versions(self):
        concept_1 = self.get_version_1_concept()
        concept_2 = self.get_version_2_concept()

        if not concept_1 or not concept_2:
            return None, None

        version_1 = Version.objects.get_for_object(concept_1).order_by('-revision__date_created').first().pk
        version_2 = Version.objects.get_for_object(concept_2).order_by('-revision__date_created').first().pk
        return (version_1, version_2)

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)
        self.context.update({"form": self.get_form()})
        
        return self.context