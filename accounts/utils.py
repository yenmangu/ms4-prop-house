from typing import Any

from accounts.reports import UserInventoryPDF
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from warehouse.models import HireRecord


def generate_user_inventory_pdf_response(
    user_id: int,
    client_name: str,
    queryset: QuerySet[HireRecord],
    *args,
    **kwargs,
) -> HttpResponse:
    """
    Transforms filtered HireRecord queryset into structured row matrix.
    Returns rendered binary PDF response.
    """

    headers: list[str] = [
        "REF ID",
        "PROP EQUIPMENT NAME",
        "ORDER REFERENCE",
        "HIRE STATUS",
    ]

    rows: list[list[Any]] = []

    for r in queryset:
        order_ref = (
            f"#{r.order_item.order.pk}"
            if r.order_item and r.order_item.order
            else "N/A"
        )
        prop_name = getattr(
            r.stock_item.product, "name", str(r.stock_item)
        )

        rows.append(
            [
                str(r.pk),
                prop_name,
                order_ref,
                r.alert_level_label,
            ]
        )

        # Dynamic context params for print layour styling

        filename = f"prop_house_manifest_{client_name}"

        pdf_context = {
            "client_name": client_name,
            "generated_at": timezone.now().strftime("%Y-%m-%d %H:%M"),
        }

        report = UserInventoryPDF(
            filename=filename,
            headers=headers,
            data_rows=rows,
            context=pdf_context,
        )

        report.title = "Your Account Asset Manifest"

        # Return evaluated Django HttpResponse object
        return report.render()
