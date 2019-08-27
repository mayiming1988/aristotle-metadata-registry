from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from aristotle_mdr_api.v4.permissions import AuthCanViewEdit, UnAuthenticatedUserCanView
from aristotle_mdr_api.v4.concepts import serializers
from aristotle_mdr.models import _concept, concept, aristotleComponent, SupersedeRelationship
from aristotle_mdr.contrib.publishing.models import VersionPermissions
from aristotle_mdr.perms import user_can_edit
from aristotle_mdr.contrib.links.utils import get_links_for_concept

from django.db.models import Q
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

import collections
from re import finditer
import reversion
from typing import List

from aristotle_mdr_api.v4.concepts.serializers import (
    ConceptSerializer,
    SupersedeRelationshipSerialiser
)
from aristotle_mdr_api.v4.views import ObjectAPIView
from aristotle_mdr import perms

import logging
logger = logging.getLogger(__name__)


class MetadataCreationView(generics.RetrieveAPIView):
    permission_classes = (UnAuthenticatedUserCanView,)

    permission_key = 'metadata'

    serializer_class = serializers.ConceptSerializer
    queryset=_concept.objects.all()