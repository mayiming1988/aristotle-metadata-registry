from django.conf.urls import url
from aristotle_mdr.contrib.publishing import views


urlpatterns = [
    url(r'^item/(?P<iid>\d+)/publish_versions/?$', views.VersionPublishMetadataFormView.as_view(), name='edit_version_history_visibility'),
    url(r'^publish/(?P<model_name>\w+)/(?P<iid>\d+)?$', views.PublishContentFormView.as_view(), name='publish_item'),
]
