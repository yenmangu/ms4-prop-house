from typing import Any
from commerce.utils.admin_invoice_pdf_response import (
    generate_admin_invoice_pdf_response,
)
from django.contrib import admin
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from commerce.models import Order, OrderItem
from core.utils.admin_link import get_admin_link
from django.utils.safestring import mark_safe


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "full_name",
        "email",
        "user",
        "total_price",
        "status",
        "created_at",
        "invoice_document_actions",
        "link_stripe_transaction",
    ]

    list_filter = ["status", "created_at"]
    search_fields = [
        "id",
        "full_name",
        "email",
        "stripe_pid",
    ]
    ordering = ["-created_at"]

    def get_urls(self):
        urls = super().get_urls()
        custom_routing = [
            path(
                "<int:order_id>/compile-invoice-pdf/",
                self.admin_site.admin_view(
                    self.process_admin_invoice_download
                ),
                name="commerce-order-invoice-pdf",
            )
        ]

        return custom_routing + urls

    def process_admin_invoice_download(
        self, request: HttpRequest, order_id: int
    ) -> HttpResponse:
        """
        Protects PDF Invoice generation logic from non-staff.
        """

        if not request.user.is_staff:
            self.message_user(
                request,
                "ACCESS DENIED // Staff Permissions Required.",
                level="error",
            )
            return HttpResponseRedirect("../")

        order = get_object_or_404(Order, pk=order_id)
        return generate_admin_invoice_pdf_response(order=order)

    def invoice_document_actions(self, obj: Order) -> str:
        """
        Renders anchor button directly within admin data rows.
        """
        url = reverse(
            "admin:commerce-order-invoice-pdf",
            args=[obj.pk],
        )

        rendered_html = render_to_string(
            "admin/partials/_invoice_button.html",
            {
                "download_url": url,
            },
        )

        # `mark_safe` used because
        # `render_to_string` already returns `SafeText`
        return mark_safe(rendered_html)

    invoice_document_actions.short_description = (
        "Billing & Accounting"
    )

    @admin.display(description="Stripe Transaction")
    def link_stripe_transaction(self, obj: "Order"):
        """
        Generates a direct link to the Stripe Dashboard
        for this Order's payment.
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
