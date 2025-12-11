from django.apps import AppConfig

class ArtistsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.artists'

    def ready(self):
        import apps.artists.signals  # This connects the signals
