from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit
from aristotle_mdr_api.v4.concepts import serializers
from aristotle_mdr.models import _concept, concept, aristotleComponent, SupersedeRelationship
from django.shortcuts import get_object_or_404
from aristotle_mdr import models as MDR
import collections
from django.db.models import Q
from aristotle_mdr_api.v4.concepts.serializers import ConceptSerializer, SupersedeRelationshipSerialiser
from aristotle_mdr import perms
from django.core.exceptions import PermissionDenied
from re import finditer
import logging
logger = logging.getLogger(__name__)


class ConceptView(generics.RetrieveAPIView):
    permission_classes=(AuthCanViewEdit,)
    permission_key='metadata'
    serializer_class=serializers.ConceptSerializer
    queryset=_concept.objects.all()


class SupersedesGraphicalConceptView(APIView):
    """Retrieve a Graphical Representation of the Supersedes Relationships"""
    permission_classes=(AuthCanViewEdit,)
    permission_key = 'metadata'
    pk_url_kwarg = 'pk'

    def get_object(self):
        id = self.kwargs[self.pk_url_kwarg]
        obj = get_object_or_404(MDR._concept, pk=id).item
        if not perms.user_can_view(self.request.user, obj):
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
                if perms.user_can_view(self.request.user, current_item):
                    serialised_item = ConceptSerializer(current_item).data
                    serialised_item["node_options"] = {"shape": "ellipse", "borderWidth": 2, "margin": 3,
                                                       "font": {"size": 15}}
                    nodes.append(serialised_item)

            if current_item.superseded_by_items_relation_set.first():
                for sup_by_rel in current_item.superseded_by_items_relation_set.all():
                    newer = sup_by_rel.newer_item
                    if newer.id not in seen_items_ids:
                        if perms.user_can_view(self.request.user, current_item):
                            nodes.append(ConceptSerializer(newer).data)
                            queue.append(newer)
                            seen_items_ids.add(newer.id)

            for sup_rel in current_item.superseded_items_relation_set.all():
                if sup_rel.older_item.id not in seen_items_ids:
                    if perms.user_can_view(self.request.user, current_item):
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

        json_response = {'nodes': nodes, 'edges': edges}

        return Response(
            json_response,
            status=status.HTTP_200_OK
        )


class GeneralGraphicalConceptView(APIView):
    """Retrieve a Graphical Representation of the General Relationships"""
    permission_classes = (AuthCanViewEdit,)
    permission_key = 'metadata'
    pk_url_kwarg = 'pk'

    def get_object(self):
        id = self.kwargs[self.pk_url_kwarg]
        obj = get_object_or_404(MDR._concept, pk=id).item
        if not perms.user_can(self.request.user, obj, 'can_view'):
            raise PermissionDenied
        return obj

    def get(self, request, pk, format=None):
        item = self.get_object()

        seen_items_ids = set()
        queue = collections.deque([item])
        nodes = []
        edges = []

        source_item = ConceptSerializer(item).data
        source_item["type"] = self.camel_case_split(item.__class__.__name__)
        source_item["node_options"] = {"shape": "ellipse", "borderWidth": 2, "margin": 3,
                                                   "font": {"size": 15}}
        nodes.append(source_item)

        if hasattr(item, 'relational_attributes'):
            for rel_attr in item.relational_attributes[0]:
                if perms.user_can_view(self.request.user, rel_attr):
                    serialised_rel_attr = ConceptSerializer(rel_attr).data
                    serialised_rel_attr["type"] = self.camel_case_split(rel_attr.__class__.__name__)
                    nodes.append(serialised_rel_attr)
                    edges.append(({"from": serialised_rel_attr["id"], "to": item.id}))

        for field in item._meta.get_fields():
            if field.is_relation and field.many_to_one and issubclass(field.related_model, concept):
                related_concept_instance = getattr(item, field.name)
                if related_concept_instance is not None:
                    if perms.user_can_view(self.request.user, related_concept_instance):
                        serialised_concept = ConceptSerializer(related_concept_instance).data
                        serialised_concept["type"] = self.camel_case_split(related_concept_instance.__class__.__name__)
                        nodes.append(serialised_concept)
                        edges.append({"from": item.id, "to": serialised_concept["id"]})
            if field.is_relation and field.one_to_many and issubclass(field.related_model, aristotleComponent):
                for aris_comp_field in field.related_model._meta.get_fields():
                    if aris_comp_field.is_relation and aris_comp_field.many_to_one and\
                            issubclass(aris_comp_field.related_model, concept) and aris_comp_field.related_model != type(item):
                        queryset = getattr(item, field.get_accessor_name()).all()
                        for component in queryset:
                            component_instance = getattr(component, aris_comp_field.name)
                            if component_instance is not None:
                                serialised_concept_instance = ConceptSerializer(component_instance).data
                                serialised_concept_instance["type"] = self.camel_case_split(component_instance.__class__.__name__)
                                nodes.append(serialised_concept_instance)
                                edges.append({"from": serialised_concept_instance["id"], "to": item.id})

        json_response = {'nodes': nodes, 'edges': edges}

        return Response(
            json_response,
            status=status.HTTP_200_OK
        )

    @staticmethod
    def camel_case_split(identifier):
        matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return ' '.join([m.group(0) for m in matches])
