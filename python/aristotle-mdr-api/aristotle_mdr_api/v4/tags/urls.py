from django.urls import path

from aristotle_mdr_api.v4.tags import views

urlpatterns = [
    path('item/<int:iid>/', views.ItemTagUpdateView.as_view(), name='item_tags'),
    path('<int:pk>/', views.TagView.as_view(), name='tags'),
]
