from django.conf.urls import url
from aristotle_mdr_api.v4.custom_fields import views

urlpatterns = [
    url(r'(?P<pk>\d+)/$', views.CustomFieldRetrieveView.as_view(), name='custom_field_get'),
    url(r'list/$', views.CustomFieldListView.as_view(), name='custom_field_list')
]
