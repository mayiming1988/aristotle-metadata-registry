from rest_framework import generics
from aristotle_mdr.contrib.issues.models import Issue

from aristotle_mdr_api.v4 import serializers, permissions
from aristotle_mdr.perms import user_can_view


class IssueView(generics.RetrieveUpdateAPIView):
    serializer_class=serializers.IssueSerializer


class IssueCreateView(generics.CreateAPIView):
    serializer_class=serializers.IssueSerializer
