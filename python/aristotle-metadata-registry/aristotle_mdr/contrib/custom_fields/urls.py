from django.conf.urls import url
from aristotle_mdr.contrib.custom_fields import views


urlpatterns = [
    url(r'^fields/edit/$', views.CustomFieldMultiEditView.as_view(), name='edit'),
    url(r'^fields/list/$', views.CustomFieldListView.as_view(), name='list'),
    url(r'^fields/(?P<pk>\d+)/delete/$', views.CustomFieldDeleteView.as_view(), name='delete'),
]
