from django.urls import path
from rest_framework import generics
from . import views
from aristotle_mdr.utils import get_concept_models
from aristotle_mdr_api.v3.views.utils import ConceptResultsPagination
from aristotle_mdr_api.v4.permissions import UnAuthenticatedUserCanView
from aristotle_mdr_api.v4.metadata.utils import create_model_api_class_dynamically


def create_metadata_urls_dynamically():
    """
    This function generates a list of valid Django URLs each of them containing a custom View class.
    The main purpose of this function is to generate serializers for the Swagger API endpoints, and
    provide a frontend graphical representation of the serializers.
    None of these endpoints are actually used, because the metadata_type parameter of the
    list_or_create_metadata_endpoint is actually overridden by the model_name of each one of the
    dynamically-generated urls.
    :return: List of paths.
    """
    list_of_urls = []
    for model in get_concept_models():
        model_name = model.__name__.lower()
        list_of_urls.extend([
            path(model_name,
                 create_model_api_class_dynamically(
                     model,
                     (generics.ListCreateAPIView,),
                     {"lookup_field": 'uuid',
                      "lookup_url_kwarg": 'item_uuid',
                      "pagination_class": ConceptResultsPagination,
                      "permission_classes": (UnAuthenticatedUserCanView,)  # TODO: We need to change the permission classes.
                      }
                 ).as_view(),
                 name='list_or_create_metadata_endpoint_' + model_name),
            path(model_name + '/<uuid:item_uuid>',
                 create_model_api_class_dynamically(
                     model,
                     (generics.UpdateAPIView,),
                     {"lookup_field": 'uuid',
                      "lookup_url_kwarg": 'item_uuid',
                      "permission_classes": (UnAuthenticatedUserCanView,)  # TODO: We need to change the permission classes.
                      }
                 ).as_view(),
                 name='retrieve_update_metadata_endpoint_' + model_name),
        ]
        )
    return list_of_urls


urlpatterns = [
    path('<uuid:item_uuid>/', views.GetMetadataTypeFromUuidAndRedirect.as_view(), name='get_metadata_type_from_uuid'),
    path('<str:metadata_type>/<uuid:item_uuid>/', views.GenericMetadataSerialiserAPIView.as_view(), name='generic_metadata_serialiser_api_endpoint'),
] + create_metadata_urls_dynamically()
