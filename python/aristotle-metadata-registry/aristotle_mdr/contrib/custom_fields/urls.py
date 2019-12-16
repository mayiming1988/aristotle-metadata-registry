from django.urls import path, re_path
from aristotle_mdr.contrib.custom_fields import views


urlpatterns = [
    path('fields/edit/', views.CustomFieldListCreateView.as_view(), name='edit'),
    path('fields/edit/<metadata_type>/', views.CustomFieldEditCreateView.as_view(), name='edit'),
    # path('fields/list/', views.CustomFieldListView.as_view(), name='list'),
    path('fields/list/<str:content_type>', views.CustomFieldListView.as_view(), name='list'),
    path('fields/<int:pk>/delete/', views.CustomFieldDeleteView.as_view(), name='delete'),
]
