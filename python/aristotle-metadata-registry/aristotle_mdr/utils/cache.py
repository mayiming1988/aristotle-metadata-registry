from typing import List
from django.contrib.contenttypes.models import ContentType
from django.apps import apps as regapps

# from aristotle_mdr.models import _concept


def recache_types(apps=None) -> List[str]:
    """
    Reset the _type field for all concepts
    Returns a list of app labels for models that were updated
    """

    if apps is None:
        apps = regapps

    # Get this from apps so it will work in migrations
    _concept = apps.get_model('aristotle_mdr', '_concept')

    updated = []

    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            # If model is a concept subclass
            if issubclass(model, _concept) and model is not _concept:
                ct = ContentType.objects.get_for_model(model)
                # Get all concepts for this model
                concepts = _concept.objects.filter(
                    id__in=model.objects.all().values_list('_concept_ptr_id', flat=True)
                )
                # Bulk update all _type fields on these concepts
                concepts.update(_type=ct)
                # Add label to updated list
                updated.append(model._meta.label_lower)

    return updated
