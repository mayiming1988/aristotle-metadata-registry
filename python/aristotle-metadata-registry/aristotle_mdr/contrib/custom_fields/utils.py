from random import randrange


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
