from django.views.generic import TemplateView
from aristotle_mdr import models as MDR
from aristotle_mdr.views.utils import SimpleItemGet
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from aristotle_mdr.contrib.links.utils import get_links_for_concept
from aristotle_mdr_api.v4.concepts.serializers import ConceptSerializer


class ItemGraphView(TemplateView, SimpleItemGet):
    model = MDR._concept
    template_name = "aristotle_mdr/graphs/item_graphs.html"
    pk_url_kwarg = 'iid'

    def get(self, request, *args, **kwargs):
        item = self.get_item(request.user)
        self.item = item
        return super(ItemGraphView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['activetab'] = 'graphs'
        context['hide_item_actions'] = True
        context['item'] = self.item.item
        return context


def link_json_for_item(request, iid):
    item = get_object_or_404(MDR._concept, pk=iid).item
    # links = get_links_for_concept(item)

    # nodes = []
    # edges = []
    # for link in links:
    #     for end in link.linkend_set.all():
    #         if 'concept_%s' % end.concept.id not in [i['id'] for i in nodes]:
    #             if end.concept == item.concept:
    #                 nodes.append({
    #                     'id': 'concept_%s' % end.concept.id,
    #                     'label': end.concept.name,
    #                     'group': 'active',
    #                     'title': "<i>This item</i>",
    #                 })
    #             else:
    #                 nodes.append({
    #                     'id': 'concept_%s' % end.concept.id,
    #                     'label': end.concept.name,
    #                     'group': 'regular',
    #                     'title': '<a href="%s">%s</a>' % (end.concept.get_absolute_url(), end.concept.name),
    #                 })
    #         if end.concept == item.concept:
    #             edges.append({
    #                 'to': 'link_%s_%s' % (link.relation.id, link.id),
    #                 'from': 'concept_%s' % end.concept.id,
    #                 # 'label': end.role.name
    #             })
    #         else:
    #             edges.append({
    #                 'from': 'link_%s_%s' % (link.relation.id, link.id),
    #                 'to': 'concept_%s' % end.concept.id,
    #                 # 'label': end.role.name
    #                 'title': end.role.name
    #             })
    #     if 'link_%s_%s' % (link.relation.id, link.id) not in [i['id'] for i in nodes]:
    #         nodes.append({
    #             'id': 'link_%s_%s' % (link.relation.id, link.id),
    #             'label': link.relation.name,
    #             'group': 'relation',
    #             'title': '<a href="%s">%s</a>' % (link.relation.get_absolute_url(), link.relation.definition),
    #         })

    return JsonResponse({
        # 'nodes': nodes,
        # 'edges': edges
        'hello': "world"
    })
