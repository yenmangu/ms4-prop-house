from django.contrib import admin
from .models import HireRecord, StockItem


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
