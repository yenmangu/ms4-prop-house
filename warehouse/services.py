from __future__ import annotations
from datetime import timedelta
from typing import TYPE_CHECKING, List
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from .models import HireRecord, StockItem
from commerce.models import Order, OrderItem

if TYPE_CHECKING:
    from catalogue.models import Product


class StockfulfilmentError(ValueError):
    """
    Raised when an orderr tries to claim stock that is no longer available.
    """

    pass


def fulfill_order_items(order: Order) -> bool:
    """
    Service Layer: Translate a 'paid' order into a physical warehouse task.

    Logic: for every `OrderItem` in the paid Order:
    create N `HireRecords`, where N is quantity.
    """

    with transaction.atomic():

        all_hire_records = []
        stock_units_to_update = []

        for item in order.items.all():
            # DEBUG: Uncomment for stock availability debug
            # stock_item = StockItem.objects.filter(
            #     product=item.product
            # ).first()
            # print(f"Item found: {stock_item}")

            # Lock rows
            available_stock = list(
                StockItem.objects.select_for_update().filter(
                    product=item.product,
                    status=StockItem.StockStatus.AVAILABLE,
                )[: item.quantity]
            )

            # DEBUG: Uncomment for stock availability debug
            # print(f"Available Stock: {available_stock}")

            if len(available_stock) < item.quantity:
                actual_phys_count = StockItem.objects.filter(
                    product=item.product,
                    status=StockItem.StockStatus.AVAILABLE,
                ).count()

                raise StockfulfilmentError(
                    f"fulfilment failed for '{item.product.name}'. "
                    f"Requested: {item.quantity}, Available: {len(available_stock)}"
                    f"Actual pysical count: {actual_phys_count}"
                )

            for stock_unit in available_stock:
                # Prepare HireRecord
                all_hire_records.append(
                    HireRecord(
                        order_item=item,
                        stock_item=stock_unit,
                        out_date=item.start_date or timezone.now(),
                        due_date=item.end_date
                        or timezone.now() + timedelta(days=7),
                    )
                )
                # Queue item for status update
                stock_unit.status = StockItem.StockStatus.ON_HIRE
                stock_units_to_update.append(stock_unit)

        if all_hire_records:
            HireRecord.objects.bulk_create(all_hire_records)

        if stock_units_to_update:
            StockItem.objects.bulk_update(
                stock_units_to_update, ["status"]
            )

        # Finalise order status
        order.status = Order.OrderStatus.PAID

    return True


def get_stock_availability(product: Product) -> dict:
    """
    Service Layer: Calculate the physical health of a product line.
    Aggregate based on status field, which is updated in  `fulfill_order_items`

    Returns:
        dict: {
            'total': Total physical assets,
            'on_hire': Total assets currently on hire,
            'available': Assets ready for a new order,
            'maintenance': Assets under maintenance
        }
    """

    stats = StockItem.objects.filter(product=product).aggregate(
        total=Count("id"),
        available=Count(
            "id", filter=Q(status=StockItem.StockStatus.AVAILABLE)
        ),
        on_hire=Count(
            "id", filter=Q(status=StockItem.StockStatus.ON_HIRE)
        ),
        maintenance=Count(
            "id", filter=Q(status=StockItem.StockStatus.MAINTENANCE)
        ),
    )

    return {
        "total": stats["total"] or 0,
        "on_hire": stats["on_hire"] or 0,
        "available": stats["available"] or 0,
        "maintenance": stats["maintenance"] or 0,
    }


def dispatch_hire_records(
    hire_record_ids: List[int], condition: str = "Good"
) -> int:
    """
    Marks physical items as having left the 'warehouse'
    """
    updated = HireRecord.objects.filter(
        id__in=hire_record_ids,
        out_date__isnull=True,
    ).update(
        out_date=timezone.now(),
        condition_on_out=condition,
    )
    return updated
