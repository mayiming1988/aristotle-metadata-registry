from django.conf.urls import include, url

urlpatterns = [
    url(r'^custom_fields/', include('aristotle_mdr_api.v4.custom_fields.urls')),
    url(r'^tags/', include('aristotle_mdr_api.v4.tags.urls')),
    url(r'^issues/', include('aristotle_mdr_api.v4.issues.urls', namespace='issues')),
    url(r'^reviews/', include('aristotle_mdr_api.v4.reviews.urls', namespace='reviews')),
]
