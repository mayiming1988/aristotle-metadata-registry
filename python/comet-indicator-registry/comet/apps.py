from aristotle_mdr.apps import AristotleExtensionBaseConfig

class CometIndicatorConfig(AristotleExtensionBaseConfig):
    name = 'comet'
    verbose_name = "Comet Indicator Registry"
    description = "Comet Indicator Registry adds a number of content type for recording additional metadata for tracking the performance of health institutes."
    create_page_name = "Performance Indicator Managment Objects"

    create_page_description = """
        These metadata types are useful for recording metadata used in the monitoring of the performance of health institutes.
    """
    create_page_priority = 50
