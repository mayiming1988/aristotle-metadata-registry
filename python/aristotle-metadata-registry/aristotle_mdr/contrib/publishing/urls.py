from django.conf.urls import url
from aristotle_mdr.contrib.publishing import views


urlpatterns = [
    url(r'^item/(?P<iid>\d+)/publishing/?$', views.PublishMetadataFormView.as_view(), name='item_publish_details'),
]
