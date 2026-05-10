from .models import Order
from warehouse import services as warehouse
from basket.models import Basket


def fulfill_order(stripe_intent_id, basket_id=None) -> bool:
    """
    Extracted utility for order fulfillment.
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
        Basket.objects.filter(id=basket_id).update(status=Basket.Status.SUBMITTED)

    # TODO: Check refactor doesnt encounter ghost basket,
    # and then remove deprecated (below)

    # order_queryset = Order.objects.filter(stripe_pid=stripe_intent_id)
    # order = order_queryset.first()

    # # Safety check
    # if order and order.status != Order.OrderStatus.PAID:
    #     order_queryset.update(status=Order.OrderStatus.PAID)

    #     # Clear associated basket ONLY when marked PAID
    #     if basket_id:
    #         Basket.objects.filter(id=basket_id).first().lines.all().delete()

    #         return True

    # return False
