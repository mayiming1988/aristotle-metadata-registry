from django.urls import path
from aristotle_mdr.contrib.custom_fields import views


urlpatterns = [
    path('fields/edit/', views.CustomFieldListCreateView.as_view(), name='edit'),
    path('fields/edit/<metadata_type>/', views.CustomFieldEditCreateView.as_view(), name='edit'),
    path('fields/<int:pk>/delete/', views.CustomFieldDeleteView.as_view(), name='delete'),
]
