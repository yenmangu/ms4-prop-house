from typing import TYPE_CHECKING

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils import timezone
from .models import HireRecord, StockItem
from .services import dispatch_hire_records
from core.utils.admin_link import get_admin_link

if TYPE_CHECKING:
    from commerce.models import Order

    obj: HireRecord


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number",
        "product",
        "status",
    )
    list_filter = (
        "status",
        "product",
    )
    search_fields = (
        "serial_number",
        "product__name",
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Logic: If we are editing an existing item (obj is not None),
        we make the product read-only to prevent historical data corruption.
        """

        if obj:
            return ("product",)
        return ()


@admin.action(
    description="Mark selected items as DISPATCHED",
)
def update_due_date(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[HireRecord],
) -> None:
    """
    Update hire record due date
    """


def mark_as_dispatched(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[HireRecord],
) -> None:
    """
    Uses warehouse service to dispatch items
    """
    queryset.update(out_date=timezone.now())
    ids = list(
        queryset.values_list(
            "id",
            flat=True,
        )
    )
    count = dispatch_hire_records(
        ids,
        condition="Dispatched via Admin",
    )
    modeladmin.message_user(
        request, f"Successfully dispatched {count} items."
    )


@admin.register(HireRecord)
class HireRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "link_order",
        "link_user",
        "link_order_item",
        "link_stock_item",
        "out_date",
        "due_date",
    )

    list_filter = (
        "out_date",
        "due_date",
        "order_item__order__user__email",
    )

    readonly_fields = ("order_item",)

    list_select_related = (
        "order_item__order",
        "stock_item",
    )

    @admin.display(
        description="Customer", ordering="order_item__order__user"
    )
    def get_customer(self, obj: "HireRecord"):
        """
        Get User by traversing relationship:
        HireRecord -> OrderItem -> Order -> User
        """

        try:
            order = obj.order_item.order
            if order.user:
                return order.user.email
            return f"{order.email} (Guest)"
        except AttributeError:
            return "No User"

    @admin.display(
        description="Customer Email",
        ordering="order_item__order__user__email",
    )
    def link_user(self, obj: "HireRecord"):
        """
        Create link between HireRecord and related User via the Order
        """
        try:
            user = obj.order_item.order.user
            if user:
                email = user.email
                url = reverse(
                    "admin:accounts_user_change", args=[user.pk]
                )
                return get_admin_link(
                    url=url,
                    label=str(email),
                )
        except AttributeError:
            pass

        return "Guest/No User"

    @admin.display(
        description="Order ID", ordering="order_item__order__id"
    )
    def link_order(self, obj: "HireRecord"):
        """
        Create link between HireRecord and related Order
        """
        if obj.order_item and obj.order_item.order:
            order_id = obj.order_item.order.pk
            url = reverse(
                "admin:commerce_order_change", args=[order_id]
            )
            return get_admin_link(
                url=url,
                label=f"Order#{order_id}",
            )
        return "No Order"

    @admin.display(
        description="Order Item", ordering="order_item__pk"
    )
    def link_order_item(self, obj: "HireRecord"):
        """
        Create link between HireRecord and associated OrderItem.
        """

        try:
            order_item = obj.order_item
            if order_item:
                id = order_item.pk
                url = reverse(
                    "admin:commerce_orderitem_change", args=[id]
                )
                return get_admin_link(
                    url=url,
                    label=f"Order Item ID: {id}",
                )
        except AttributeError:
            pass
        return "No associated Order Item"

    @admin.display(
        description="Stock Item", ordering="stock_item__serial_number"
    )
    def link_stock_item(self, obj: "HireRecord"):
        """
        Create link between HireRecord and related StockItem.
        Truncates the returned label to keep dasboard clean.
        """

        TRUNC_VAL = 10

        if obj.stock_item:
            url = reverse(
                "admin:warehouse_stockitem_change",
                args=[obj.stock_item.pk],
            )
            return get_admin_link(
                url=url,
                label=truncatechars(str(obj.stock_item), TRUNC_VAL),
                hover_text=str(obj.stock_item),
            )
        return "Unassigned"

    actions = [mark_as_dispatched]
