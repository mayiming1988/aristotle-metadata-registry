from django.conf import settings
from django.urls import path, include


urlpatterns = [
    path('alias/', include('impersonate.urls')),
    path('api/', include('aristotle_mdr_api.urls')),
    path('', include(('aristotle_dse.urls', "aristotle_dse"), namespace="aristotle_dse")),
    path('', include(('aristotle_mdr.contrib.links.urls', "aristotle_mdr_links"), namespace="aristotle_mdr_links")),
    path('', include(('aristotle_mdr.contrib.slots.urls', "aristotle_slots"), namespace="aristotle_slots")),
    path('', include(('aristotle_mdr.contrib.identifiers.urls', "aristotle_mdr_identifiers"), namespace="aristotle_identifiers")),
    path('', include('aristotle_mdr.urls')),
    path('', include(('aristotle_mdr.contrib.links.urls', "aristotle_mdr_links"), namespace="aristotle_mdr_links")),
    path('comet/', include(('comet.urls', "comet"), namespace='comet')),
    path('glossary/', include(('aristotle_glossary.urls', "aristotle_glossary"), namespace="aristotle_glossary")),
]


if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))


# This is only for dev work, so we can skip it.
if settings.DEBUG:  # pragma: no cover
    from django.contrib.staticfiles import views

    urlpatterns += [
        path('static/<path:path>', views.serve),
    ]

    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
