from aristotle_mdr.apps import AristotleExtensionBaseConfig


class Config(AristotleExtensionBaseConfig):
    name = 'aristotle_mdr.contrib.aristotle_backwards'
    label = 'aristotle_mdr_backwards'
    verbose_name = 'Aristotle Backwards Compatibility'
    create_page_name = "ISO 11179 Edition 2 Backwards Compatibility Objects"
    create_page_description = """
        These metadata types provide backwards compatible support to record information
        captured in metadata registries that must conform to Edition 2 of the ISO 11179 standard
        for metadata registies.
    """
    create_page_priority = 50
