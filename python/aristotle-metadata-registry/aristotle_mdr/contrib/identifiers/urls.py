from django.urls import path
from aristotle_mdr.contrib.identifiers.views import scoped_identifier_redirect, namespace_redirect


urlpatterns = [
    path('identifier/<str:ns_prefix>/<str:identifier>/<str:version>', scoped_identifier_redirect, name='scoped_identifier_redirect_version'),
    path('identifier/<str:ns_prefix>/<str:identifier>', scoped_identifier_redirect, name='scoped_identifier_redirect'),
    path('identifier/<str:ns_prefix>', namespace_redirect, name='namespace_redirect'),
]
