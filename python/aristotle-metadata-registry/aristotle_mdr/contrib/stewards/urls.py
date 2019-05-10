from django.conf.urls import url, include
from aristotle_mdr.models import StewardOrganisationMembership, StewardOrganisation
# from .views import
from .views import views, manager

urlpatterns = [
    url(
        r'', include(
            manager.group_backend_factory().get_urls(),
            namespace="group"
        ),
    ),
]
