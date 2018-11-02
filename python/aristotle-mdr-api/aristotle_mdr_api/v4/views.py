from rest_framework import generics
from aristotle_mdr.contrib.issues.models import Issue

from aristotle_mdr_api.v4 import serializers, permissions


class IssueView(generics.RetrieveUpdateAPIView):
    serializer_class=serializers.IssueSerializer
    permission_classes=(permissions.IssuePermission,)


class IssueCreateView(generics.CreateAPIView):
    serializer_class=serializers.IssueSerializer
    permission_classes=(permissions.IssuePermission,)
