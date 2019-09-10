from django.urls import path, re_path
from aristotle_mdr.contrib.custom_fields import views


urlpatterns = [
    path('fields/edit/', views.CustomFieldEditableOptionsList, name='list_options'),
    path('fields/edit/<metadata_type>/', views.CustomFieldModelEditView.as_view(), name='edit'),
    re_path(r'^fields/list/$', views.CustomFieldListView.as_view(), name='list'),
    re_path(r'^fields/(?P<pk>\d+)/delete/$', views.CustomFieldDeleteView.as_view(), name='delete'),
]
