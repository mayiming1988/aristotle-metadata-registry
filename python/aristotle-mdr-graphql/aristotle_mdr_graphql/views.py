from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.contrib.auth.models import AnonymousUser

from aristotle_mdr_api.token_auth.mixins import TokenAuthMixin
from aristotle_mdr_graphql.schema.schema import schema  # Is that enought schema

from graphene_django.views import GraphQLView
from graphql.error import format_error
import json

import logging
logger = logging.getLogger(__name__)


class FancyGraphQLView(GraphQLView):
    default_query = ""

    def __init__(self, *args, **kwargs):
        self.default_query = kwargs.pop("default_query", "")
        super().__init__(*args, **kwargs)

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        if 'html' in request.content_type or not request.content_type:
            if "noexplorer" not in request.GET.keys() and "raw" not in request.GET.keys():
                return redirect("aristotle_graphql:graphql_explorer")
        return super().dispatch(request, *args, **kwargs)

    def render_graphiql(self, request, **data):
        # If there is no query we want to render something useful
        data['query'] = data.get("query") or self.default_query
        return render(request, self.graphiql_template, data)


class ExternalGraphqlView(TokenAuthMixin, View):
    """
    View for external applications to query graphql
    Token authentication is required to view private content
    This view is marked as csrf_exempt
    """
    permission_key = 'graphql'
    check_read_only = True

    def execute_query(self, request, query, variables):
        result = schema.execute(query, context=request, variables=variables)
        if result.errors:
            return JsonResponse({'errors': [format_error(e) for e in result.errors]})
        else:
            return JsonResponse({'data': result.data})

    def post(self, request, *args, **kwargs):
        # If a token was submitted set the request user to the user whos token was submitted
        if self.token_user:
            request.user = self.token_user
        else:
            # Force anon user if token auth was not used
            request.user = AnonymousUser()

        try:
            body = request.body.decode()
        except UnicodeError:
            return HttpResponseBadRequest('Request body was not valid unicode')

        variables = {}

        # This is adapted from GraphQLView's parse_body method
        if request.content_type == 'application/json':
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return HttpResponseBadRequest('Request body was not valid json')

            variables = data.get('variables', {})
            query = data.get('query', '')
        elif request.content_type == 'application/graphql':
            query = body
        else:
            # 415 is Unsupported Media Type
            return HttpResponse('Invalid Content-Type, must be applicaton/json or application/graphql', status=415)

        return self.execute_query(request, query, variables)
