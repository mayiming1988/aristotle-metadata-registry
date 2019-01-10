from django.apps import AppConfig


class AristotleExtensionBaseConfig(AppConfig):
    from aristotle_mdr import checks


class AristotleMDRConfig(AristotleExtensionBaseConfig):
    name = 'aristotle_mdr'
    verbose_name = "Aristotle Metadata Registry"

    def ready(self):
        pass
