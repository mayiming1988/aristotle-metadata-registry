from django.conf.urls import include, url
from ..views import concepts, views, concepttypes, about
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register(r'metadata', concepts.ConceptViewSet)
router.register(r'types', concepttypes.ConceptTypeViewSet)
router.register(r'search', views.SearchViewSet, base_name="search")
router.register(r'ras', views.RegistrationAuthorityViewSet)
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'superseded_by', concepts.SupersededRelationshipViewSet)
# router.register(r'about', about.About)


urlpatterns = [
    url(r'^$', get_swagger_view(title='Aristotle v3 API', urlconf='aristotle_mdr_api.v3.urls')),
    url(r'^about/$', about.About.as_view()),
    url(r'^', include(router.urls)),
]
