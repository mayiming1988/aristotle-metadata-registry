from django.conf.urls import url
from aristotle_mdr_api.v4.tags import views

urlpatterns = [
    url(r'item/(?P<iid>\d+)/$', views.ItemTagUpdateView.as_view(), name='item_tags'),
    url(r'(?P<pk>\d+)/$', views.TagView.as_view(), name='tags'),
]
