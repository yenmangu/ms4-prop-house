from commerce.models import Order
from django.contrib import messages
from django.http import HttpRequest


class StockAlertMiddleware:
    """
    Checks for unacknowledged fulfillment errors and injects safely into native django.messages framework for Toast rendering.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """
        Only check authenticated accounts.
        Limit to last 5 failed orders.
        """

        if request.user.is_authenticated:
            failed_orders = Order.objects.filter(
                status=Order.OrderStatus.FAILED,
                admin_notes__isnull=False,
            )[:5]

            for order in failed_orders:
                messages.error(
                    request,
                    f"CRITICAL STOCK MISMATCH: Order #{order.pk} failed alloccation. "
                    f"Details: {order.admin_notes}",
                )
            response = self.get_response(request)
            return response
