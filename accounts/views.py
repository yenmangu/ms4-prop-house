from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView
from warehouse.models import HireRecord


class UserDashboardHireView(LoginRequiredMixin, ListView):
    """
    Displays active hre records derived from completed orders
    """

    model = HireRecord
    template_name = "accounts/dashboard.html"
    context_object_name = "hire_records"

    def get_queryset(self):
        """
        Optimised query bridging physical assets to the authenticated User
        Uses ''SQL JOIN' with `select_related` to pull all linked data
        """
        return (
            HireRecord.objects.filter(order_item__order__user=self.request.user)
            .select_related(
                "order_item",
                "stock_item__product",
                "order_item__order",
            )
            .order_by("-order_item__order__created_at")
        )
