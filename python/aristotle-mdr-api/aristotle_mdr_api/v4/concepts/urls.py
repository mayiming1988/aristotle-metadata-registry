from django.conf.urls import url
from aristotle_mdr_api.v4.concepts import views

urlpatterns = [
    url(r'(?P<pk>\d+)/$', views.ConceptView.as_view(), name='item'),
    url(r'^(?P<pk>\d+)/graphical/$', views.GraphicalConceptView.as_view(), name='item_graphical'),
]
