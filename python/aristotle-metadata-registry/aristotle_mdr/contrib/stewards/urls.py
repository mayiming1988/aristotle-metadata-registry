from django.conf.urls import url, include
# from aristotle_mdr.contrib.user_management import views, org_backends
# from aristotle_mdr.contrib.groups.backends import group_backend_factory
from aristotle_mdr.models import StewardOrganisationMembership, StewardOrganisation
# from .views import group_backend_factory
from .views import views, manager

urlpatterns = [
    # url(r'^accounts/signup', views.NewUserSignupView.as_view(), name="new_user_signup"),
    # url(r'^all/?$', views.ListStewardOrg.as_view(), name='view_all'),
    # # url(r'^create/?$', views.ListStewardOrg.as_view(), name='create'),
    url(
        r'', include(
            manager.group_backend_factory().get_urls(),
            namespace="group"
        ),
    ),
]
