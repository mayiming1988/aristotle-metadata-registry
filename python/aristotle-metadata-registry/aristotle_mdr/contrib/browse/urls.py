from django.conf.urls import url
from aristotle_mdr.contrib.browse import views

urlpatterns = [
    url(r'^apps', views.BrowseAppsView.as_view(), name='browse_apps'),
    url(r'^(?P<app>[a-zA-Z_]+)/(?P<model>[a-zA-Z_]+)/?', views.BrowseConceptsView.as_view(), name='browse_concepts'),
    url(r'^(?P<app>[a-zA-Z_]+)/?', views.BrowseModelsView.as_view(), name='browse_models'),
    url(r'^', views.BrowseStartView.as_view(), name='browse')
]
