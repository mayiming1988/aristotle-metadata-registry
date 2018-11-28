from django.conf.urls import url
from aristotle_mdr.contrib.custom_fields import views


urlpatterns = [
    url(r'^fields/create/$', views.CreateCustomFieldView.as_view(), name='create'),
]
