from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from aristotle_mdr.urls.aristotle import concept_urlpatterns as mdr_concept_urlpatterns
from aristotle_mdr.utils import fetch_aristotle_settings

import logging
logger = logging.getLogger(__name__)

admin.autodiscover()

aristotle_settings = fetch_aristotle_settings()
content_extensions = aristotle_settings.get('CONTENT_EXTENSIONS', [])

concept_urlpatterns = []

if 'aristotle_dse' in content_extensions:
    from aristotle_dse.urls import concept_urlpatterns as dse_concept_urlpatterns
    concept_urlpatterns += dse_concept_urlpatterns

concept_urlpatterns += mdr_concept_urlpatterns

base_urlpatterns = [
    url(r'^', include('aristotle_mdr.urls.base')),
    url(r'^browse/', include('aristotle_mdr.contrib.browse.urls')),
    url(r'^help/', include('aristotle_mdr.contrib.help.urls', app_name="aristotle_help", namespace="aristotle_help")),
    url(r'^', include('aristotle_mdr.contrib.user_management.urls', namespace="aristotle-user")),
    url(r'^', include('aristotle_mdr.urls.aristotle', app_name="aristotle_mdr", namespace="aristotle")),
    url(r'^ac/', include('aristotle_mdr.contrib.autocomplete.urls', namespace="aristotle-autocomplete")),
    url(r'^', include('aristotle_mdr.contrib.healthcheck.urls', app_name="aristotle_mdr_hb", namespace="aristotle_hb")),
]

logger.debug('Setting urlpatterns')
urlpatterns = concept_urlpatterns + base_urlpatterns

# This is only for dev work, so we can skip it.
if settings.DEBUG:  # pragma: no cover
    from django.contrib.staticfiles import views

    urlpatterns += [
        url(r'^static/(?P<path>.*)$', views.serve),
    ]

    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'aristotle_mdr.views.unauthorised'
handler404 = 'aristotle_mdr.views.not_found'
