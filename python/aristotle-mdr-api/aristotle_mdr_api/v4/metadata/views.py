from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet
from django.template.defaultfilters import slugify
from rest_framework.response import Response
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit, UnAuthenticatedUserCanView
from aristotle_mdr_api.v4.concepts import serializers
from aristotle_mdr.contrib.serializers.concept_serializer import ConceptSerializerFactory
from aristotle_mdr.models import _concept

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
            redirect_to=reverse("api_v4:metadata:generic_metadata_serialiser_api_endpoint",
                                kwargs={"metadata_type": slugify(item.item_type),
                                        "item_uuid": item_uuid})
        )


class GenericMetadataSerialiserAPIView(generics.ListCreateAPIView):  # CHANGE THIS ONE TO RETRIEVEUPDATEAPIVIEW.

    permission_classes = (UnAuthenticatedUserCanView,)

    def dispatch(self, request, *args, **kwargs):
        self.metadata_type = kwargs.get("metadata_type")
        self.item_uuid = kwargs.get("item_uuid")
        # item = get_object_or_404(type(self.item), uuid=self.item_uuid)
        # self.item = get_object_or_404(self.item.item_type.model_class(), uuid=self.item_uuid)

        print("THIS IS THE ITEM")
        print(self.get_object())
        # print("THIS IS THE CONTENT TYPE:")
        # print()
        # print("THIS IS THE OBJECT:")
        # new = get_object_or_404(type(self.item), uuid=self.item_uuid)
        # print(new)
        # print(type(new))

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):  # OVERRIDE GET QUERYSET!!!!
        return self.item.item_type.model_class().objects.get(uuid=self.item_uuid)

    def get_serializer(self, *args, **kwargs):
        serialiser_model = ConceptSerializerFactory().generate_serializer(self.item)
        serialiser = serialiser_model(self.item)
        return serialiser

    def update(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, data=request.data, many=True)

        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
