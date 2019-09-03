from rest_framework import generics, pagination
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.parsers import JSONParser
from django.template.defaultfilters import slugify
from rest_framework.response import Response
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from aristotle_mdr_api.v4.permissions import UnAuthenticatedUserCanView
from aristotle_mdr_api.v3.views.utils import ConceptResultsPagination
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


# Eventually we need to update this class to subclass RetrieveUpdateAPIView.
# We need to make this class capable of object deserialization for "PUT" and "PATCH" requests.
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

    # def put(self, request, *args, **kwargs):
    #     pass
    #
    # def patch(self, request, *args, **kwargs):
    #     pass


class CreateMetadata(generics.ListCreateAPIView):
    """
    The purpose of this API endpoint is to create Metadata Objects.
    """

    pagination_class = ConceptResultsPagination

    # def get_parsers(self):
    #     parsers = super().get_parsers().append(JSONParser)
    #     return parsers

    def dispatch(self, request, *args, **kwargs):
        metadata_type = kwargs.get("metadata_type")
        for model in get_concept_models():
            if slugify(model.__name__) == metadata_type:
                self.klass = model
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.klass.objects.all()

    def get_queryset(self):
        return self.klass.objects.all()

    def get_serializer_class(self):
        return ConceptSerializerFactory().generate_serializer_class(self.klass)

    # # When get is used just retrieve objects from that type.
    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)
    #
    # # When post is used try to create an object of the specified metadata type.
    # def post(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(
            queryset, data=request.data, many=True,
            context={'version_ids': "self.version_ids"}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
