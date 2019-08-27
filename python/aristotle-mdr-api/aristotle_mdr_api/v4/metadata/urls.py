from django.urls import path
from . import views

urlpatterns = [
    path(r'^$', views.MetadataCreationView.as_view(), name='create'),
]
