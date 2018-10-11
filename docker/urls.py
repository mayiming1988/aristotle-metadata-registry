from django.conf import settings
from django.conf.urls import include, url

urlpatterns = [
    url(r'^alias/', include('impersonate.urls')),
    url(r'^', include('aristotle_mdr.urls')),
]

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
