from rest_framework import generics
from rest_framework.views import APIView
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit, UnAuthenticatedUserCanView
from aristotle_mdr_api.v4.concepts import serializers
from aristotle_mdr.models import _concept

import logging
logger = logging.getLogger(__name__)


class MetadataBaseApiView:
    pass


class MetadataCreationView(APIView):
    permission_classes = (AuthCanViewEdit,)

    permission_key = 'metadata'

    serializer_class = serializers.ConceptSerializer
    queryset = _concept.objects.all()


class ObjectClassMetadataCreationView(generics.CreateAPIView):
    permission_classes = (UnAuthenticatedUserCanView,)

    permission_key = 'metadata'

    serializer_class = serializers.ConceptSerializer
    queryset = _concept.objects.all()
