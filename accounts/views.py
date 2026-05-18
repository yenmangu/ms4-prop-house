from typing import Optional, Tuple

from accounts.filters import UserOrderFilter
from accounts.models import MembershipTier, User
from accounts.services import MembershipService
from commerce.mixins import StripeMixin
from commerce.models import Order
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.functional import classproperty
from django.views import View
from django.views.generic import ListView
import stripe
from view_breadcrumbs import ListBreadcrumbMixin
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


class MembershipOptionsView(ListBreadcrumbMixin, ListView):
    """
    Renders the available premium membership plans (Indie, Content Creator, Production House) for users to view, compare and select.
    """

    model = MembershipTier
    template_name = "accounts/membership_options.html"
    context_object_name = "membership_tiers"

    @classmethod
    def list_view_name(cls):
        return "membership_options"

    @property
    def list_view_url(self):
        """
        Override the breadcrumb mixin
        """
        return reverse_lazy("accounts:membership_options")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["current_tier"] = (
                self.request.user.membership_tier
            )
        else:
            context["current_tier"] = None

        return context


class InitiateMembershipCheckoutView(
    LoginRequiredMixin, StripeMixin, View
):
    """
    Handles secure POST requests to initiate a Stripe Subscription checkout lifecycle for a targeted membership tier.
    """

    def post(self, request: HttpRequest, pk):
        """
        Post request for view
        """
        # Fetch targeted tier safely
        tier = get_object_or_404(MembershipTier, pk=pk)

        intent, error = MembershipService.create_subscription_intent(
            user=request.user,
            tier=tier,
        )
        if error:
            return JsonResponse(
                {
                    "error": f"Stripe Setup Error: {error}",
                },
                status=400,
            )

        return JsonResponse(
            {
                "clientSecret": intent.client_secret,
                "stripePK": self.stripe_public_key,
            }
        )


class MembershipSuccessView(LoginRequiredMixin, View):
    """
    Landing checkpoint verifying completed user billing flow.
    """

    def get(self, request: HttpRequest):
        messages.success(
            request, "Welcome to your new membership plan."
        )
        return redirect("accounts:membership_options")
