from aristotle_mdr.apps import AristotleExtensionBaseConfig

class AristotleGlossaryConfig(AristotleExtensionBaseConfig):
    name = 'aristotle_glossary'
    verbose_name = "Aristotle Glossary Extension"
    description = "Aristotle Glossary Extension adds an additional content type for managing glossary definitions and the UI fields necessary to easily insert them."

    create_page_name = "Business Glossary Objects"
    create_page_description = """
        The Business Glossary Extension adds an additional content type for creating and endorsing key definitions
        that can be inserted into other metadata objects using the Aristotle rich-text editor.
    """
    create_page_priority = 60
