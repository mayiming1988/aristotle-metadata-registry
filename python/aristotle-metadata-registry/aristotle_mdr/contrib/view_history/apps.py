from django.apps import AppConfig


class Config(AppConfig):
    name = 'aristotle_mdr.contrib.view_history'
    label = 'aristotle_mdr_view_history'
    verbose_name = 'Aristotle View History'

    def ready(self):
        from aristotle_mdr.contrib.view_history import signals  # noqa: F401
