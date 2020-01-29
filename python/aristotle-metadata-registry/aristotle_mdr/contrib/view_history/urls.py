from django.urls import path
from . import views


urlpatterns = [
    path('account/recently_viewed/', views.RecentlyViewedView.as_view(), name='recently_viewed_metadata'),
    path('account/recently_viewed/clear_all/', views.ClearRecentlyViewedView.as_view(), name='clear_all_recently_viewed_metadata'),
    path('account/recently_viewed/remove/<int:pk>', views.RemoveRecentlyViewedView.as_view(), name='delete_recently_viewed_metadata_item'),
]
