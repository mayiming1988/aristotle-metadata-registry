from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^', include('aristotle_mdr.urls.base')),
    url(r'^browse/', include('aristotle_mdr.contrib.browse.urls')),
    url(r'^favourites/', include('aristotle_mdr.contrib.favourites.urls', namespace="aristotle_favourites")),
    url(r'^help/', include('aristotle_mdr.contrib.help.urls', app_name="aristotle_help", namespace="aristotle_help")),
    url(r'^', include('aristotle_mdr.contrib.user_management.urls', namespace="aristotle-user")),
    url(r'^', include('aristotle_mdr.urls.aristotle', app_name="aristotle_mdr", namespace="aristotle")),
    url(r'^ac/', include('aristotle_mdr.contrib.autocomplete.urls', namespace="aristotle-autocomplete")),
    url(r'^', include('aristotle_mdr.contrib.healthcheck.urls', app_name="aristotle_mdr_hb", namespace="aristotle_hb")),
    url(r'^', include('aristotle_mdr.contrib.view_history.urls')),
    url(r'^', include('aristotle_mdr.contrib.reviews.urls', app_name="aristotle_mdr_review_requests", namespace="aristotle_reviews")),
]

handler403 = 'aristotle_mdr.views.unauthorised'
handler404 = 'aristotle_mdr.views.not_found'
handler500 = 'aristotle_mdr.views.handler500'
