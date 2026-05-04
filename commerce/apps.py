from django.apps import AppConfig


class CommerceConfig(AppConfig):
    detect_auto_field = "django.db.models.BigAutoField"
    name = "commerce"

    def ready(self) -> None:
        import commerce.signals
