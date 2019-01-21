from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from aristotle_mdr.contrib.issues.models import Issue, IssueComment
from . import serializers
from aristotle_mdr_api.v4.permissions import AuthCanViewEdit
from aristotle_mdr import perms


class IssueView(generics.RetrieveUpdateAPIView):
    """Retrive and update and issue"""
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.IssueSerializer
    queryset=Issue.objects.all()


class IssueCreateView(generics.CreateAPIView):
    """Create a new issue"""
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.IssueSerializer


class IssueCommentCreateView(generics.CreateAPIView):
    """Create a comment against an issue"""
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.IssueCommentSerializer


class IssueCommentRetrieveView(generics.RetrieveAPIView):
    """Retrieve an issue comment"""
    permission_classes=(AuthCanViewEdit,)
    serializer_class=serializers.IssueCommentSerializer
    queryset=IssueComment.objects.all()


class IssueUpdateAndCommentView(APIView):
    """Open or close an issue, with optional comment"""
    permission_classes=(AuthCanViewEdit,)
    issue_serializer=serializers.IssueSerializer
    comment_serializer=serializers.IssueCommentSerializer
    pk_url_kwarg='pk'

    def get_object(self):
        pk = self.kwargs[self.pk_url_kwarg]
        obj = get_object_or_404(Issue, pk=pk)
        if not perms.user_can(self.request.user, obj, 'can_alter_open'):
            raise PermissionDenied
        return obj

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        if 'isopen' not in request.data:
            return Response()

        serializer_context = {'request': request}
        issue_serializer = self.issue_serializer(
            instance=obj,
            data={'isopen': request.data['isopen']},
            partial=True,
            context=serializer_context
        )
        issue_serializer.is_valid()

        response_content = {}

        if 'comment' in request.data:
            commentdata = request.data['comment']
            commentdata['issue'] = obj.pk

            comment_serializer = self.comment_serializer(
                data=commentdata,
                context=serializer_context
            )
            comment_serializer.is_valid(raise_exception=True)
            comment_serializer.save()
            response_content['comment'] = comment_serializer.data

        issue_serializer.save()
        response_content['issue'] = issue_serializer.data

        return Response(
            response_content,
            status=status.HTTP_200_OK,
        )
