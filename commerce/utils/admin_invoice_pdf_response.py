from typing import Any

from commerce.models import Order
from core.utils.admin_pdf import UserInvoicePDF
from django.http import HttpResponse
from django.utils import timezone


def generate_admin_invoice_pdf_response(order: Order) -> HttpResponse:
    """
    Transforms an individual order transaction into a downloadable
    ReportLab binary tax invoice stream.
    """

    headers: list[str] = []
    rows: list[list[Any]] = []

    # Defaults
    default_full_name = "Client Account Holder"
    n_a = "N/A"

    for item in order.items.all():
        rows.append(
            [
                str(item.product_name),
                str(item.quantity),
                f"{item.line_total}",
            ]
        )

    client_name = order.full_name or default_full_name
    client_email = order.email or n_a

    context: dict[str, Any] = {
        "order_id": order.pk,
        "date": (
            order.created_at.strftime("%Y-%m-%d %H:%M")
            if order.created_at
            else timezone.now().strftime("%Y-%m-%d %H:%M")
        ),
        "cient_name": client_name,
        "client_email": client_email,
        "total_amount": f"{order.total_price}",
    }

    filename = f"invoice_INV_{order.pk}.pdf"

    report = UserInvoicePDF(
        filename=filename,
        headers=headers,
        data_rows=rows,
        context=context,
    )

    return report.render()
