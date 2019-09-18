from aristotle_mdr.apps import AristotleExtensionBaseConfig


class AristotleDSEConfig(AristotleExtensionBaseConfig):
    name = 'aristotle_dse'
    verbose_name = "Aristotle Dataset Extensions"
    description = "Aristotle Dataset Extensions adds content types for tracking data set defintions and data sources."

    create_page_name = "Data set management objects"
    create_page_description = """
        These metadata types can be used to record the existence of data catalogs, dataset and 
        metadata specifications for data using models defined by the World Wide Web Data Catalog standard.
    """
    create_page_priority = 40
