from django.urls import path
from . import views

urlpatterns = [
    path(r'^$', views.MetadataCreationView.as_view(), name='create'),
    path('objectclass/', views.ObjectClassMetadataCreationView.as_view(), name='create'),
]
