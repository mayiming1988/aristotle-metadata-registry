from django.conf.urls import url
from aristotle_mdr_api.v4.concepts import views


urlpatterns = [
    url(r'^(?P<pk>\d+)/update-permissions/$', views.UpdateVersionPermissionsView.as_view(),
        name="update-version-permissions"),
    url(r'^(?P<pk>\d+)/view-permission/(?P<vpk>\d+)/$', views.GetVersionsPermissionsView.as_view(),
        name='view-version-permissions'),
    url(r'(?P<pk>\d+)/$', views.ConceptView.as_view(), name='item'),
    url(r'^(?P<pk>\d+)/supersedes-graphical/$', views.SupersedesGraphicalConceptView.as_view(), name='item_supersedes_graphical'),
    url(r'^(?P<pk>\d+)/general-graphical/$', views.GeneralGraphicalConceptView.as_view(), name='item_general_graphical'),
    url(r'^(?P<pk>\d+)/links-graphical/$', views.ConceptLinksView.as_view(), name='api_item_links'),
    url(r'^(?P<pk>\d+)/list-versions/$', views.ListVersionsView.as_view(), name="list-versions"),
    url(r'^(?P<pk>\d+)/list-permissions/$', views.ListVersionsPermissionsView.as_view(), name="list-version-permissions"),
]
