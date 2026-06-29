from commerce.models import Order
from django.core.management import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Surgically clear commerce data and remove Order, OrderItem and ghost OrderLine tables."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING("Starting commerce purge...")
        )

        with transaction.atomic():
            with connection.cursor() as cursor:
                self.stdout.write(
                    "Dropping legacy 'commerce_orderline' table..."
                )
                cursor.execute(
                    "DROP TABLE IF EXISTS commerce_orderline CASCADE;"
                )

            order_count = Order.objects.count()
            Order.objects.all().delete()
            self.stdout.write(
                f"Purged {order_count} Order records via ORM"
            )
        self.stdout.write(
            self.style.SUCCESS("Commerce environment now clean")
        )
