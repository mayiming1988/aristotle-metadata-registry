from django.conf.urls import url
from aristotle_mdr_api.v4.custom_fields import views

urlpatterns = [
    url('(?P<pk>\d+)/$', views.CustomFieldRetrieveView.as_view())
]
