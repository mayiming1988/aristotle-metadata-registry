from django.conf.urls import url, include
# from aristotle_mdr.contrib.user_management import views, org_backends
# from aristotle_mdr.contrib.groups.backends import group_backend_factory
from aristotle_mdr.models import StewardOrganisationMembership, StewardOrganisation
from .views import group_backend_factory

urlpatterns = [
    # url(r'^accounts/signup', views.NewUserSignupView.as_view(), name="new_user_signup"),
    url(r'^steward', #include(group_backend_factory(),
        include(
            group_backend_factory(
                # group_class = StewardOrganisation,
                # membership_class = StewardOrganisationMembership,
                # namespace="aristotle_mdr:stewards:group",
            ).get_urls(),
            namespace="group"
        ),
    ),
]
