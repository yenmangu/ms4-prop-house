from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from warehouse.services import (
    StockfulfilmentError,
    fulfill_order_items,
)


@receiver(post_save, sender=Order)
def trigger_warehouse_fulfilment(
    sender, instance: Order, created: bool, **kwargs
):
    """
    Listen for Order being marked as 'PAID' and trigger warehouse service.

    Args:
        sender (ModelBase): commerce.models.Order
        instance (Order): Order Object
        created (bool): _description_
    """

    # Only trigger if status has moved to 'PAID'
    if instance.status == Order.OrderStatus.PAID:

        def safe_fulfilment_wrapper():
            try:
                fulfill_order_items(instance)
            except StockfulfilmentError as e:
                instance.status = Order.OrderStatus.FAILED

                instance.admin_notes = (
                    f"inventory allocation failed: {str(e)}"
                )

                instance.save(update_fields=["status", "admin_notes"])

        transaction.on_commit(safe_fulfilment_wrapper)
