from aristotle_mdr.apps import AristotleExtensionBaseConfig


class Config(AristotleExtensionBaseConfig):
    name = 'aristotle_mdr.contrib.links'
    label = 'aristotle_mdr_links'
    verbose_name = 'Aristotle Concept Links and Relations'
    description = """
    This module allows users of the registry to create taxonomies using custom relationships with associated roles,
    which can be used to create links between metadata items.

    For example, a user could create a "Broader than" relationship, with "broader term" and "narrower term" as the roles within the relationship.
    A new link could be made based on this relationship with the broader term end connecting to the Object Class "Person" and the narrower term end pointing to the Object Class "Employee".
    """

    create_page_name = "Relation and Link management"
    create_page_description = """
        This metadata type allows users to create custom relationships with associated roles,
        which can be used to create links between metadata items in an ISO 11179 compliant manner.
    """
    create_page_priority = 5000
