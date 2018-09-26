from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^account/recently_viewed/?$', views.RecentlyViewedView.as_view(), name='recently_viewed_metadata'),
]
