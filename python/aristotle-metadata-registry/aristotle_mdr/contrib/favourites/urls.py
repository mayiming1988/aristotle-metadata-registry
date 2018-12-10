from django.conf.urls import url
from aristotle_mdr.contrib.favourites import views

urlpatterns = [
    url(r'^toggleFavourite/(?P<iid>\d+)/?$', views.ToggleFavourite.as_view(), name='toggleFavourite'),
    url(r'^editTags/(?P<iid>\d+)/?$', views.EditTags.as_view(), name='edit_tags'),
    url(r'^savedItems/?$', views.FavouritesAndTags.as_view(), name='favs_and_tags'),
    url(r'^favourites/?$', views.FavouriteView.as_view(), name='favs'),
    url(r'^tag/(?P<tagid>\d+)/?$', views.TagView.as_view(), name='tag'),
    url(r'^allTags?$', views.AllTagView.as_view(), name='all_tags'),
]
