from django.conf.urls import url
from aristotle_mdr.contrib.custom_fields import views


urlpatterns = [
    url(r'^fields/create/$', views.CustomFieldCreateView.as_view(), name='create'),
    url(r'^fields/(?P<pk>\d+)/update/$', views.CustomFieldUpdateView.as_view(), name='update'),
    url(r'^fields/(?P<pk>\d+)/delete/$', views.CustomFieldDeleteView.as_view(), name='delete'),
    url(r'^fields/list/$', views.CustomFieldListView.as_view(), name='list'),
]
