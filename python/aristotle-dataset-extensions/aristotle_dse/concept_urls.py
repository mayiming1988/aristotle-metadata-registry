from django.conf.urls import url
from aristotle_dse.views import DatasetSpecificationView

urlpatterns = [
    url(r'^item/(?P<iid>\d+)/datasetspecification/(?P<name_slug>.+)/?$', DatasetSpecificationView.as_view(), name='datasetspecification'),
]
