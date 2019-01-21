from graphene_django.views import GraphQLView
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import AnonymousUser

from aristotle_mdr_api.token_auth.mixins import TokenAuthMixin
from aristotle_mdr_graphql.schema.schema import schema  # Is that enought schema

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
    """
    permission_key = 'graphql'
    check_read_only = True

    def execute_query(self, request, query, variables):
        result = schema.execute(query, context=request, variables=variables)
        if result.errors:
            return JsonResponse({'errors': result.errors})
        else:
            return JsonResponse({'data': result.data})

    def post(self, request, *args, **kwargs):
        # If a token was submitted set the request user to the user whos token was submitted
        if self.token_user:
            request.user = self.token_user
        else:
            # Force anon user if token auth was not used
            request.user = AnonymousUser()

        variables = {}
        query = ''

        # This is adapted from GraphQLView's parse_body method
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode())
            variables = data.get('variables', {})
            query = data.get('query', '')
        elif request.content_type == 'application/graphql':
            query = request.body.decode()
        else:
            # 415 is Unsupported Media Type
            return HttpResponse('Incorrect Content-Type', status_code=415)

        return self.execute_query(request, query, variables)
