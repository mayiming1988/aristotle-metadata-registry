from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from django.template.defaultfilters import slugify
from rest_framework.response import Response
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from aristotle_mdr_api.v4.permissions import UnAuthenticatedUserCanView
from aristotle_mdr.contrib.serializers.concept_serializer import ConceptSerializerFactory
from aristotle_mdr.models import _concept
from aristotle_mdr.utils import get_concept_models


import logging
logger = logging.getLogger(__name__)


class MetadataBaseApiView:
    pass


class GetMetadataTypeFromUUID(APIView):
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


class GenericMetadataSerialiserAPIView(generics.RetrieveUpdateAPIView):

    lookup_field = 'uuid'
    lookup_url_kwarg = 'item_uuid'

    permission_classes = (UnAuthenticatedUserCanView,)

    def dispatch(self, request, *args, **kwargs):

        self.metadata_type = kwargs.get("metadata_type")

        for model in get_concept_models():
            if slugify(model.__name__) == self.metadata_type:
                self.model_instance = model
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model_instance.objects.all()

    def get_serializer(self, *args, **kwargs):
        serialiser_model = ConceptSerializerFactory().generate_serializer(self.get_object())
        serialiser = serialiser_model(self.get_object())
        return serialiser

    def update(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, data=request.data, many=True)

        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
