from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from .models import HireRecord, StockItem
from .services import dispatch_hire_records


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
        "get_order_id",
        "order_item",
        "stock_item",
        "out_date",
        "due_date",
    )

    list_filter = (
        "out_date",
        "due_date",
    )

    readonly_fields = ("order_item",)

    list_select_related = (
        "order_item__order",
        "stock_item",
    )

    actions = [mark_as_dispatched]
