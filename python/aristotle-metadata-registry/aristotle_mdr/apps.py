from django.apps import AppConfig


class AristotleExtensionBaseConfig(AppConfig):
    create_page_priority = 500
    create_page_name = ""
    verbose_name = "No Name"


class AristotleMDRConfig(AristotleExtensionBaseConfig):
    name = 'aristotle_mdr'
    verbose_name = "Aristotle Metadata Registry"
    create_page_name = "Basic Metadata Registry Objects"
    create_page_description = """
        These metadata types provide the core pieces for describing information
        recorded in a metadata registry.
    """
    create_page_priority = 0

    def ready(self):
        from aristotle_mdr import checks
