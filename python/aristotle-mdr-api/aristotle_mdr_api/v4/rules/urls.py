from django.conf.urls import url
from aristotle_mdr_api.v4.rules import views

urlpatterns = [
    url(r'ra/$', views.CreateRARules.as_view(), name='create_ra_rules'),
    url(r'ra/(?P<id>\d+)/$', views.RetrieveUpdateRARules.as_view(), name='ra_rules'),
    url(r'registry/$', views.RetrieveUpdateRegistryRules.as_view(), name='registry_rules'),
]
