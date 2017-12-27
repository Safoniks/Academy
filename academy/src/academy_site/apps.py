from django.apps import AppConfig


class AcademySiteConfig(AppConfig):
    name = 'academy_site'

    def ready(self):
        import academy_site.signals.user_signals
