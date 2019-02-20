from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit
from aristotle_mdr_api.v4.concepts import serializers
from aristotle_mdr.models import _concept
from django.shortcuts import redirect, get_object_or_404
from aristotle_mdr import models as MDR
import collections
from django.db.models import Q
from aristotle_mdr_api.v4.concepts.serializers import ConceptSerializer, SupersedeRelationshipSerialiser
from aristotle_mdr.models import SupersedeRelationship
from django.http import HttpResponseRedirect, JsonResponse
from aristotle_mdr import perms
from django.core.exceptions import PermissionDenied
import logging
logger = logging.getLogger(__name__)


class ConceptView(generics.RetrieveAPIView):
    permission_classes=(AuthCanViewEdit,)
    permission_key='metadata'
    serializer_class=serializers.ConceptSerializer
    queryset=_concept.objects.all()


class GraphicalConceptView(APIView):
    """Retrieve a Graphical Representation of the Supersedes Relationships"""
    permission_classes=(AuthCanViewEdit,)
    permission_key = 'metadata'
    pk_url_kwarg = 'pk'

    def get_object(self):
        id = self.kwargs[self.pk_url_kwarg]
        obj = get_object_or_404(MDR._concept, pk=id).item
        if not perms.user_can(self.request.user, obj, 'can_alter_open'):
            raise PermissionDenied
        return obj

    def get(self, request, pk, format=None):
        item = self.get_object()

        seen_items_ids = set()
        queue = collections.deque([item])
        nodes = []
        edges = []
        q_objects = Q()

        while queue and len(queue) < 50:
            current_item = queue.popleft()
            if current_item.id not in seen_items_ids:
                serialised_item = ConceptSerializer(current_item).data
                serialised_item["node_options"] = {"shape": "ellipse", "borderWidth": 2, "margin": 3,
                                                   "font": {"size": 18}}
                nodes.append(serialised_item)

            if current_item.superseded_by_items_relation_set.first():
                newer = current_item.superseded_by_items_relation_set.first().newer_item
                if newer.id not in seen_items_ids:
                    if newer.can_view(user):
                        nodes.append(ConceptSerializer(newer).data)
                        queue.append(newer)
                    seen_items_ids.add(newer.id)

            for sup_rel in current_item.superseded_items_relation_set.all():
                older_item = sup_rel.older_item
                if sup_rel.older_item.id not in seen_items_ids:
                    if older_item.can_view(user):
                        nodes.append(ConceptSerializer(older_item).data)
                        queue.append(older_item)
                    seen_items_ids.add(older_item.id)
            seen_items_ids.add(current_item.id)

        seen_items_ids = list(seen_items_ids)

        for item in seen_items_ids:
            q_objects.add(Q(older_item__id=item), Q.OR)
            q_objects.add(Q(newer_item__id=item), Q.OR)

        supersede_relationships_queryset = SupersedeRelationship.objects.filter(q_objects)

        for item in supersede_relationships_queryset:
            edges.append(SupersedeRelationshipSerialiser(item).data)

        json_response = {'nodes': nodes, 'edges': edges}

        return Response(
            json_response,
            status=status.HTTP_200_OK
        )



