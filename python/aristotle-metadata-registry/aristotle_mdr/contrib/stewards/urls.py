from django.conf.urls import url, include
from .views import manager

urlpatterns = [
    url(
        r'', include(
            (manager.group_backend_factory().get_urls(), 'aristotle_mdr.contrib.stewards'),
            namespace="group"
        ),
    ),
    # url(
    #     # CHECK - Can I do this? Instead of the commented out code?
    #     r'', manager.group_backend_factory().get_urls,
    # ),
    # url(
    #     r'', include(
    #         manager.group_backend_factory().get_urls(),
    #         namespace="group"
    #     ),
    # ),
]
