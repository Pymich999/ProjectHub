from django.apps import AppConfig


class MbookhubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mbookhub'

    def ready(self):
        import mbookhub.signals
