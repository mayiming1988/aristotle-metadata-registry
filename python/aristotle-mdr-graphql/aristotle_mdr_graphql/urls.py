from django.urls import path
from aristotle_mdr_graphql.schema.schema import schema
from aristotle_mdr_graphql.views import FancyGraphQLView, ExternalGraphqlView, GraphQLWrapperView
from django.views.decorators.csrf import csrf_exempt
from textwrap import dedent

urlpatterns = [
    path('', GraphQLWrapperView.as_view(), name='graphql_explorer'),
    path('api', FancyGraphQLView.as_view(
        graphiql=True,
        schema=schema,
        default_query=dedent("""
            # This query fetches the name of the first 5 metadata items you
            # have permission to see
            # Use the documentation on the right to build further queries

            query {
              metadata (first: 5) {
                edges {
                  node {
                    name
                    definition
                  }
                }
              }
            }
            """)
    ), name='graphql_api'),
    path('json', csrf_exempt(ExternalGraphqlView.as_view()), name='external')
]
