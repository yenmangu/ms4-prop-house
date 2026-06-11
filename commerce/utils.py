from .models import Order
from warehouse import services as warehouse
from basket.models import Basket


def fulfill_order(stripe_intent_id, basket_id=None) -> bool:
    """
    Extracted utility for order fulfilment.
    Marks order as PAID and clears associated basket.
    Returns True when marked as PAID and False if order not found.
    """

    order = Order.objects.filter(stripe_pid=stripe_intent_id).first()
    if not order or order.status == Order.OrderStatus.PAID:
        return

    # Trigger warehouse allocation
    # Updating to PAID triggers the signal to call `warehouse.fulfill_order`
    order.status = Order.OrderStatus.PAID
    order.save()

    if basket_id:
        # Close basket
        Basket.objects.filter(id=basket_id).update(
            status=Basket.Status.SUBMITTED
        )
