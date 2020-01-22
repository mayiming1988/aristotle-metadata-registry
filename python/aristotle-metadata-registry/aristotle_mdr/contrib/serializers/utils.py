"""A collection of util functions to help """
from aristotle_mdr.models import aristotleComponent


def get_concept_fields(model_class):
    fields = []
    for field in model_class._meta.get_fields():
        if not field.is_relation:
            if not field.name.startswith('_'):
                # Don't serialize internal fields
                fields.append(field)

    return fields


def get_concept_field_names(model_class):
    """Get fields that are actually **on** the model.
       Returns a tuple of fields"""
    fields = get_concept_fields(model_class)
    return tuple([field.name for field in fields])


def get_field_name(field):
    if hasattr(field, 'get_accessor_name'):
        return field.get_accessor_name()
    else:
        return field.name


def get_relation_fields(model_class):
    """
    Helper function to get related fields
    Returns a tuple of fields
    """
    related_fields = []
    for field in model_class._meta.get_fields():
        if not field.name.startswith('_'):
            # Don't serialize internal fields
            if field.is_relation:
                # Check if the model class is the parent of the item, we don't want to serialize up the chain
                field_model = field.related_model
                if issubclass(field_model, aristotleComponent):
                    # If it's a subclass of aristotleComponent it should have a parent
                    parent_model = field_model.get_parent_model()
                    if not parent_model:
                        # This aristotle component has no parent model
                        related_fields.append(field)
                    else:
                        if field_model.get_parent_model() == model_class:
                            # If the parent is the model we're serializing, right now
                            related_fields.append(field)
                        else:
                            # It's the child, we don't want to serialize
                            pass
                else:
                    # Just a normal field
                    related_fields.append(field)

    return related_fields


def get_relation_field_names(model_class, whitelisted_fields=None):
    fields = get_relation_fields(model_class)
    if whitelisted_fields:
        return tuple([get_field_name(field) for field in fields if field in whitelisted_fields])
    else:
        return tuple([get_field_name(field) for field in fields])
