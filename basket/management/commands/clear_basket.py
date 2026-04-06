from django.core.management.base import BaseCommand
from basket.models import Basket, Line


class Command(BaseCommand):
    help = "Wipes all Basket and Line data to reset development state"

    def handle(self, *args, **kwargs):
        line_count = Line.objects.count()
        basket_count = Basket.objects.count()

        self.stdout.write(
            self.style.WARNING(
                f"Deleting {line_count} lines and {basket_count} baskets..."
            )
        )

        Line.objects.all().delete()
        Basket.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Successfully cleared manifest data."))
