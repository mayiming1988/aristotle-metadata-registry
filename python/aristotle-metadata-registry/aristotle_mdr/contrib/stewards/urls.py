from django.conf.urls import url, include
from aristotle_mdr.contrib.user_management import views, org_backends
from aristotle_mdr.contrib.groups.backends import group_backend_factory
from aristotle_mdr.models import OrganisationAccountMembership, OrganisationAccount

urlpatterns = [
    # url(r'^accounts/signup', views.NewUserSignupView.as_view(), name="new_user_signup"),
    url(r'^steward',
        include(
            group_backend_factory(
                group_class = OrganisationAccount,
                membership_class = OrganisationAccountMembership,
                # url_path = "steward",
                namespace="aristotle_mdr:stewards:group",
                update_fields = ['slug', 'name', 'description']
            ).get_urls(),
            namespace="group"
        ),
    ),
]
