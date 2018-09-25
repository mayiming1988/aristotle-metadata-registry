from django.conf.urls import url
from aristotle_dse import views

urlpatterns = [
    url(r'^item/(?P<iid>\d+)/datasetspecification/(?P<name_slug>.+)/?$', views.DatasetSpecificationView.as_view(), name='datasetspecification'),
]
