from __future__ import annotations
from typing import TYPE_CHECKING, List
from django.db import transaction
from .models import HireRecord

if TYPE_CHECKING:
    from commerce.models import Order, OrderItem


def fulfill_order_items(order: Order) -> bool:
    """
    Service Layer: Translate a 'paid' order into a physical warehouse task.

    Logic: for every `OrderItem` in the paid Order:
    create N `HireRecords`, where N is quantity.
    """

    with transaction.atomic():

        for item in order.items.all():

            records_to_create: List[HireRecord] = [
                HireRecord(
                    order_item=item,
                )
                for _ in range(item.quantity)
            ]

            HireRecord.objects.bulk_create(records_to_create)
    return True
