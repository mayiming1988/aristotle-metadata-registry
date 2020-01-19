def get_concept_fields(self, model_class):
    """Get fields that are actually **on** the model.
       Returns a tuple of fields"""
    fields = []
    for field in model_class._meta.get_fields():
        # If data field or foreign key field
        if not field.is_relation or field.many_to_one:
            if not field.name.startswith('_'):
                # Don't serialize internal fields
                fields.append(field.name)

    return tuple(fields)