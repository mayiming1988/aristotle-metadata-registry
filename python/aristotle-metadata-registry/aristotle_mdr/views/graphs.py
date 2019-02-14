from django.views.generic import TemplateView
from aristotle_mdr import models as MDR
from aristotle_mdr.views.utils import SimpleItemGet
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from aristotle_mdr.contrib.links.utils import get_links_for_concept
from aristotle_mdr_api.v4.concepts.serializers import ConceptSerializer, SupersedeRelationshipSerialiser
from rest_framework.renderers import JSONRenderer
import logging
from django.db.models import Q
from aristotle_mdr.models import SupersedeRelationship
import collections

logger = logging.getLogger(__name__)


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
    #
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

    seen_items_ids = set()
    # process = []
    queue = collections.deque([item])
    nodes = []
    edges = []
    q_objects = Q()

    ################
    # # OPTION 1 (NOT OPTIMISED):
    # process.append(item)
    # while process:
    #     current_item = process.pop()
    #     if current_item.id not in seen_items_ids:
    #         nodes.append(ConceptSerializer(current_item).data)
    #     for sup_by_rel in current_item.superseded_by_items_relation_set.all():
    #         supersede_relationship = SupersedeRelationshipSerialiser(sup_by_rel).data
    #         if supersede_relationship not in edges:
    #             edges.append(supersede_relationship)
    #
    #         newer = sup_by_rel.newer_item
    #         if newer.id not in seen_items_ids:
    #             nodes.append(ConceptSerializer(newer).data)
    #             process.append(newer)
    #             seen_items_ids.add(newer.id)
    #
    #     for sup_rel in current_item.superseded_items_relation_set.all():
    #         super_rel = SupersedeRelationshipSerialiser(sup_rel).data
    #         if super_rel not in edges:
    #             edges.append(super_rel)
    #         if sup_rel.older_item.id not in seen_items_ids:
    #             nodes.append(ConceptSerializer(sup_rel.older_item).data)
    #             process.append(sup_rel.older_item)
    #             seen_items_ids.add(sup_rel.older_item.id)
    #     seen_items_ids.add(current_item.id)
    #
    #################

    #################
    # OPTION 2 (OPTIMISED):
    # process.append(item)
    while queue and len(queue) < 50:
        current_item = queue.popleft()
        if current_item.id not in seen_items_ids:
            serialised_item = ConceptSerializer(current_item).data
            serialised_item["node_options"] = {"shape": "ellipse", "borderWidth": 2, "margin": 3, "font": {"size": 18}}
            nodes.append(serialised_item)

        if current_item.superseded_by_items_relation_set.first():
            newer = current_item.superseded_by_items_relation_set.first().newer_item
            if newer.id not in seen_items_ids:
                nodes.append(ConceptSerializer(newer).data)
                queue.append(newer)
                seen_items_ids.add(newer.id)

        for sup_rel in current_item.superseded_items_relation_set.all():
            if sup_rel.older_item.id not in seen_items_ids:
                nodes.append(ConceptSerializer(sup_rel.older_item).data)
                queue.append(sup_rel.older_item)
                seen_items_ids.add(sup_rel.older_item.id)
        seen_items_ids.add(current_item.id)

    seen_items_ids = list(seen_items_ids)

    for item in seen_items_ids:
        q_objects.add(Q(older_item__id=item), Q.OR)
        q_objects.add(Q(newer_item__id=item), Q.OR)

    supersede_relationships_queryset = SupersedeRelationship.objects.filter(q_objects)

    for item in supersede_relationships_queryset:
        edges.append(SupersedeRelationshipSerialiser(item).data)
    #################

    return JsonResponse({
        'nodes': nodes,
        'edges': edges,
    })
