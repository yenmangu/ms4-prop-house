from commerce.models import Order, OrderItem
from core.utils import get_admin_link
from django.contrib import admin


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_price",
        "link_stripe_transaction",
    )

    @admin.display(description="Stripe Transaction")
    def link_stripe_transaction(self, obj: "Order"):
        """
        Generates a direct link to the Stripe Dashboard for this Order's payment.
        """
        # TODO: Add stripe test mode flag
        prefix = "test/"
        stripe_id = getattr(obj, "stripe_pid", None)
        if stripe_id:
            url = f"https://dashboard.stripe.com/{prefix}payments/{stripe_id}"

            return get_admin_link(url, "View in Stripe ↗")
        return "N/A"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass
