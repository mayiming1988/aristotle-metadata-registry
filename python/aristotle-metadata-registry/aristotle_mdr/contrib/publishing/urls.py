from django.conf.urls import url
from aristotle_mdr.contrib.publishing import views


urlpatterns = [
    url(r'^item/(?P<iid>\d+)/publishing/?$', views.VersionPublishMetadataFormView.as_view(), name='item_publish_details'),
    url(r'^publish/(?P<model_name>\w+)/(?P<iid>\d+)?$', views.PublishContentFormView.as_view(), name='publish_item'),
]
