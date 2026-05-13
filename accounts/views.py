from accounts.filters import UserOrderFilter
from commerce.models import Order
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
        qs = (
            HireRecord.objects.filter(
                order_item__order__user=self.request.user
            )
            .select_related(
                "stock_item__product", "order_item__order"
            )
            .order_by("-order_item__order__created_at")
        )
        self.filterset = UserOrderFilter(
            self.request.GET, queryset=qs
        )

        return self.filterset.qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # Make template context aware
        context["zone"] = "dashboard"

        # Initialise qs
        qs = self.get_queryset()
        base_qs = self.filterset.qs

        # Assign context
        context["filter"] = self.filterset
        context["active_hires"] = base_qs.filter(
            returned_date__isnull=True,
            out_date__isnull=False,
        )
        context["returned_hires"] = base_qs.filter(
            returned_date__isnull=False
        )

        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return "accounts/partials/_user_hire_data.html"
        return "accounts/dashboard.html"
