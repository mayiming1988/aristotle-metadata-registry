from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:item_uuid>/', views.GetMetadataTypeFromUUID.as_view(), name='get_metadata_type_from_uuid'),
    path('<str:metadata_type>/<uuid:item_uuid>/', views.GenericMetadataSerialiserAPIView.as_view(), name='generic_metadata_serialiser_api_endpoint'),
    path('<str:metadata_type>/', views.CreateMetadata.as_view(), name='create_metadata_endpoint'),
]
