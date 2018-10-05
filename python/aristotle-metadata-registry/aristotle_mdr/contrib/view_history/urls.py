from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^account/recently_viewed/?$', views.RecentlyViewedView.as_view(), name='recently_viewed_metadata'),
    url(r'^account/recently_viewed/clear_all/?$', views.ClearRecentlyViewedView.as_view(), name='clear_all_recently_viewed_metadata'),
    url(r'^account/recently_viewed/remove/(?P<pk>\d+)?$', views.RemoveRecentlyViewedView.as_view(), name='delete_recently_viewed_metadata_item'),
]
