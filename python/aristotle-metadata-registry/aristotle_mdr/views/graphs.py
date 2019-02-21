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
