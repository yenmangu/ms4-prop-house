from .models import Order
from basket.models import Basket


def fulfill_order(stripe_intent_id, basket_id=None) -> bool:
    """
    Extracted utility for order fulfillment.
    Marks order as PAID and clears associated basket.
    Returns True when marked as PAID and False if order not found.
    """

    order_queryset = Order.objects.filter(stripe_pid=stripe_intent_id)
    order = order_queryset.first()

    # Safety check
    if order and order.status != Order.OrderStatus.PAID:
        order_queryset.update(status=Order.OrderStatus.PAID)

        # Clear associated basket ONLY when marked PAID
        if basket_id:
            Basket.objects.filter(id=basket_id).first().lines.all().delete()

            return True

    return False
