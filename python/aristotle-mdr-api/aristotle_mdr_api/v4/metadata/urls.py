from django.urls import path
from . import views
from aristotle_mdr.utils import get_concept_models
from aristotle_mdr.contrib.serializers.concept_serializer import ConceptSerializerFactory


def create_model_api_class_dynamically(model):
    return type(
        model.__class__.__name__.capitalize() + "ListOrCreateMetadata",
        (views.ListOrCreateMetadata,),
        {
            "serializer_class": ConceptSerializerFactory().generate_serializer_class(model),
            '__doc__': "\n{}".format(model.__doc__.replace('\n\n', '\n'))
         }
    )


def create_metadata_urls_dynamically():
    list_of_urls = []
    for model in get_concept_models():
        model_name = model.__name__.lower()
        list_of_urls.append(
            path(model_name + '/', create_model_api_class_dynamically(model).as_view(), name='list_or_create_metadata_endpoing_' + model_name))
    return list_of_urls


urlpatterns = [
    path('<uuid:item_uuid>/', views.GetMetadataTypeFromUUID.as_view(), name='get_metadata_type_from_uuid'),
    path('<str:metadata_type>/<uuid:item_uuid>/', views.GenericMetadataSerialiserAPIView.as_view(), name='generic_metadata_serialiser_api_endpoint'),
    path('<str:metadata_type>/', views.ListOrCreateMetadata.as_view(), name='list_or_create_metadata_endpoint'),
] + create_metadata_urls_dynamically()






