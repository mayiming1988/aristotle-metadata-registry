from django.urls import path
from aristotle_mdr.contrib.identifiers.views import scoped_identifier_redirect, namespace_redirect


urlpatterns = [
    path('identifier/<path:ns_prefix>/<path:iid>/<path:version>', scoped_identifier_redirect, name='scoped_identifier_redirect_version'),
    path('identifier/<path:ns_prefix>/<path:iid>', scoped_identifier_redirect, name='scoped_identifier_redirect'),
    path('identifier/<path:ns_prefix>', namespace_redirect, name='namespace_redirect'),
]
