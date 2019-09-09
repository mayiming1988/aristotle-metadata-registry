from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from django.template.defaultfilters import slugify
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from aristotle_mdr_api.v3.views.utils import ConceptResultsPagination
from aristotle_mdr.contrib.serializers.concept_serializer import ConceptSerializerFactory
from aristotle_mdr.models import _concept
from aristotle_mdr_api.v4.permissions import UnAuthenticatedUserCanView
from aristotle_mdr.utils import get_concept_models


import logging
logger = logging.getLogger(__name__)


class MetadataBaseApiView:
    pass


class GetMetadataTypeFromUuidAndRedirect(APIView):
    """
    The purpose of this API Endpoint is to retrieve the item type from a uuid parameter and redirect to a
    generic metadata serialiser API Endpoint handler.
    """
    permission_classes = (UnAuthenticatedUserCanView,)

    def dispatch(self, request, *args, **kwargs):
        item_uuid = kwargs.get("item_uuid")
        item = get_object_or_404(_concept, uuid=item_uuid)

        return HttpResponseRedirect(
            redirect_to=reverse(
                "api_v4:metadata:generic_metadata_serialiser_api_endpoint",
                kwargs={
                    "metadata_type": slugify(item.item_type.model),
                    "item_uuid": item_uuid,
                }
            )
        )


class GenericMetadataSerialiserAPIView(generics.RetrieveAPIView):
    """
    The purpose of this API Endpoint is to retrieve a serializer from a _concept metadata child instance.
    """

    lookup_field = 'uuid'
    lookup_url_kwarg = 'item_uuid'
    permission_classes = (UnAuthenticatedUserCanView,)

    def dispatch(self, request, *args, **kwargs):

        metadata_type = kwargs.get("metadata_type")

        for model in get_concept_models():
            if slugify(model.__name__) == metadata_type:
                self.klass = model
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.klass.objects.all()

    def get_serializer(self, instance, *args, **kwargs):
        serializer_class = ConceptSerializerFactory().generate_serializer_class(self.klass)
        return serializer_class(instance)
