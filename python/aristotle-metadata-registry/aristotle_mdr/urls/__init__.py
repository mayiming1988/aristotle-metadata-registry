from django.conf import settings
from django.urls import path, re_path, include
from django.contrib import admin
import notifications.urls

admin.autodiscover()

urlpatterns = [
    path('', include(('aristotle_mdr.contrib.issues.urls', 'aristotle_mdr.contrib.issues'), namespace='aristotle_issues')),
    path('', include(('aristotle_mdr.contrib.publishing.urls', 'aristotle_mdr_publishing'), namespace="aristotle_publishing")),
    path('', include('aristotle_mdr.urls.base')),
    path('browse/', include('aristotle_mdr.contrib.browse.urls')),
    path('favourites/', include(('aristotle_mdr.contrib.favourites.urls', 'aristotle_mdr.contrib.favourites'), namespace='aristotle_favourites')),
    path('help/', include(('aristotle_mdr.contrib.help.urls', 'aristotle_help'), namespace="aristotle_help")),
    path('', include(('aristotle_bg_workers.urls', 'aristotle_bg_workers'), namespace='aristotle_bg_workers')),
    path('', include(('aristotle_mdr.contrib.user_management.urls', 'aristotle_mdr.contrib.user_management'), namespace='aristotle-user')),
    path('', include(('aristotle_mdr.urls.aristotle', 'aristotle_mdr'), namespace="aristotle")),
    path('ac/', include(('aristotle_mdr.contrib.autocomplete.urls', 'aristotle_mdr.contrib.autocomplete'), namespace='aristotle-autocomplete')),
    path('', include('aristotle_mdr.contrib.view_history.urls')),
    path('', include(('aristotle_mdr.contrib.reviews.urls', 'aristotle_mdr_review_requests'), namespace="aristotle_reviews")),
    path('', include(('aristotle_mdr.contrib.custom_fields.urls', 'aristotle_mdr.contrib.custom_fields'), namespace='aristotle_custom_fields')),
    path('', include(('aristotle_mdr.contrib.validators.urls', 'aristotle_mdr.contrib.validators'), namespace='aristotle_validations')),
    path('api/', include('aristotle_mdr_api.urls')),
    re_path('account/notifications/', include((notifications.urls, 'notifications'), namespace="notifications")),
]

if settings.DEBUG:
    from aristotle_mdr.views import debug as debug_views
    urlpatterns += [
        re_path(r'^aristotle_debug/(pdf|word|html|slow)/$', debug_views.download, name='api_mark_all_read'),
    ]

handler403 = 'aristotle_mdr.views.unauthorised'
handler404 = 'aristotle_mdr.views.not_found'
handler500 = 'aristotle_mdr.views.handler500'
