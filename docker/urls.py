from django.conf import settings
from django.conf.urls import include, url

urlpatterns = [
    url(r'^alias/', include('impersonate.urls')),
    url(r'^', include('aristotle_mdr.contrib.slots.urls', app_name="aristotle_slots", namespace="aristotle_slots")),
    url(r'^', include('aristotle_mdr.contrib.links.urls', app_name="aristotle_mdr_links", namespace="aristotle_mdr_links")),
    url(r'^', include('aristotle_dse.urls', app_name="aristotle_dse", namespace="aristotle_dse")),
    url(r'^', include('aristotle_mdr.urls')),
]

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
