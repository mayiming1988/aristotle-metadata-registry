from django.conf.urls import url
from aristotle_mdr_api.v4.concepts import views

urlpatterns = [
    url(r'(?P<pk>\d+)/$', views.ConceptView.as_view(), name='item'),
    url(r'^(?P<pk>\d+)/supersedes-graphical/$', views.SupersedesGraphicalConceptView.as_view(), name='item_supersedes_graphical'),
    url(r'^(?P<pk>\d+)/general-graphical/$', views.GeneralGraphicalConceptView.as_view(), name='item_general_graphical'),
]