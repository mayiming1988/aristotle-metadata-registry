from django.conf.urls import url
from aristotle_mdr.contrib.autocomplete import views

urlpatterns = [
    url(
        r'^relation$',
        views.RelationAutocomplete.as_view(),
        name='relation'
    ),
    url(
        r'^concept/(?:(?P<app_name>[a-z_]+)-(?P<model_name>[a-z_]+))?$',
        views.GenericConceptAutocomplete.as_view(),
        name='concept',
    ),
    url(
        r'^user$',
        views.UserAutocomplete.as_view(),
        name='user',
    ),
    url(
        r'^workgroup',
        views.WorkgroupAutocomplete.as_view(),
        name='workgroup',
    ),
    url(
        r'^framework',
        views.FrameworkDimensionsAutocomplete.as_view(),
        name='framework'
    ),
    url(
        r'^(?P<soid>\d+)/collection',
        views.CollectionAutocomplete.as_view(),
        name='collection'
    ),
]
