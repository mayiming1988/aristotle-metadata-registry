from django.conf.urls import url
from aristotle_mdr.contrib.publishing import views


urlpatterns = [
    url(r'^publish/(?P<model_name>\w+)/(?P<iid>\d+)?$', views.PublishContentFormView.as_view(), name='publish_item'),
    url(r'^registry/publish/(?P<model_name>\w+)/(?P<iid>\d+)?$', views.PublishRegistryContentFormView.as_view(), name='publish_registry_item'),
]
