from random import randrange
from aristotle_mdr.utils.utils import get_content_type_to_concept_name


def get_system_name(allowed_model, name) -> str:
    """Gets the system name of the Custom Field """
    if allowed_model is None:
        allowed_model = 'all'
    else:
        allowed_model = str(allowed_model.model).replace(' ', '')

    # Make the name lowercase and strip spaces
    name = name.replace(" ", "").lower()

    system_name = '{namespace}:{name}'.format(namespace=allowed_model,
                                              name=name)
    return system_name


def generate_random_unique_characters() -> int:
    """Generate random unique characters to append at the end of a system name if it is not unique"""
    return randrange(10, 100)


def get_name_of_edited_model(metadata_type):
    mapping = get_content_type_to_concept_name()
    if metadata_type in mapping:
        return mapping[metadata_type]
    return 'All Models'
