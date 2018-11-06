from rest_framework import generics
from aristotle_mdr.contrib.issues.models import Issue

from aristotle_mdr_api.v4 import serializers
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit, AuthFinePerms


class IssueView(generics.RetrieveUpdateAPIView):
    permission_classes=(AuthFinePerms,)
    serializer_class=serializers.IssueSerializer
    queryset=Issue.objects.all()


class IssueCreateView(generics.CreateAPIView):
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.IssueSerializer


class IssueCommentCreateView(generics.CreateAPIView):
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.IssueCommentSerializer

    def create(self, request, *args, **kwargs):
        request.data['issue'] = self.kwargs['issuepk']
        return super().create(request, *args, **kwargs)
