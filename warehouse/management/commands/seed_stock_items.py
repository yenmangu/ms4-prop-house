from typing import List

from catalogue.models import Product
from django.core.management import BaseCommand
from django.core.management.base import OutputWrapper
from django.db.models import QuerySet
from warehouse.models import StockItem


class Command(BaseCommand):
    """
    _Domain:_ Warehouse

    Synchronises the physical inventory to the stock levels defined in
    `catalogue.Product`.

    In this architechture, a Product is an abstract entry, whereas a `StockItem`
    is a tangible asset.

    This command materialises those physical assets, generating a unique
    serial number for every item to have individual traceability.

    To be used during development and at anytime the warehouse needs resetting to
    'factory' state.

    _Usage_
    `python manage.py seed_stock_items`

    """

    help = "Generates physical StockItem entries based on Product.stock_quantity"

    def handle(self, *args, **options):
        products: QuerySet[Product] = Product.objects.filter(
            is_hire=True,
            stock_quantity__gt=0,
        )

        total_created: int = 0
        success_style: OutputWrapper = self.style.SUCCESS

        for product in products:
            # Type hint for development peace
            product: Product
            current_count = product.stock_items.count()
            needed = product.stock_quantity - current_count

            if needed <= 0:
                self.stdout.write(
                    success_style(f"Skipping {product.name}: Stock already satisfied")
                )
                continue
            self.stdout.write(
                success_style(f"Seeding {needed} units for {product.name}...")
            )

            new_items: List[StockItem] = []
            for i in range(needed):
                # Robust Serial: [SLUG-4]-[ID]-[INDEX]
                serial: str = (
                    f"{product.slug.upper()[:4]}-{product.id}-{current_count + i +1:04d}"
                )

                new_items.append(
                    StockItem(
                        product=product,
                        serial_number=serial,
                        status=StockItem.StockStatus.AVAILABLE,
                    )
                )

            StockItem.objects.bulk_create(new_items)
            total_created += len(new_items)
            self.stdout.write(
                success_style(
                    f"Successfully added {len(new_items)} units to {product.name}"
                )
            )
        self.stdout.write(
            success_style(f"Task complete. Total StockItems created: {total_created}")
        )
