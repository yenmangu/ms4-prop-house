from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from warehouse.services import fulfill_order_items


@receiver(post_save, sender=Order)
def trigger_warehouse_fulfillment(sender, instance: Order, created: bool, **kwargs):
    """
    Listen for Order being marked as 'PAID' and trigger warehouse service.

    Args:
        sender (ModelBase): commerce.models.Order
        instance (Order): Order Object
        created (bool): _description_
    """

    # Only trigger if status has moved to 'PAID'
    if instance.status == Order.OrderStatus.PAID:
        fulfill_order_items(instance)
