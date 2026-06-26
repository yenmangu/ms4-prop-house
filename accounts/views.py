import json
from typing import Optional, Tuple

from accounts.filters import UserOrderFilter
from accounts.models import MembershipTier, User
from accounts.services import MembershipService
from accounts.utils import generate_user_inventory_pdf_response
from commerce.mixins import StripeMixin
from commerce.models import Order
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy

from django.views import View
from django.views.generic import ListView
import stripe
from view_breadcrumbs import ListBreadcrumbMixin
from warehouse.models import HireRecord


class UserDashboardHireView(
    LoginRequiredMixin, ListBreadcrumbMixin, ListView
):
    """
    Displays active hre records derived from completed orders
    UPDATE: supports raw binary PDF rendering.
    """

    model = HireRecord
    app_name = "accounts"
    template_name = "accounts/dashboard.html"
    context_object_name = "hire_records"

    crumbs = [
        ("My Bookings", None),
    ]

    def get_queryset(self):
        """
        Optimised query bridging physical assets to the authenticated User
        Uses ''SQL JOIN' with `select_related` to pull all linked data.
        UPDATE: Utilises for_dashboard_users layer,
        so no need for previous deprecated code
        """

        qs = HireRecord.objects.for_dashboard_user(self.request.user)

        # All of the deprecated code is now encapsulated in `for_dashboard_users`

        # qs = (
        #     HireRecord.objects.filter(
        #         order_item__order__user=self.request.user
        #     )
        #     .select_related(
        #         "stock_item__product", "order_item__order"
        #     )
        #     .with_alert_levels()
        #     .order_by("-order_item__order__created_at")
        # )

        self.filterset = UserOrderFilter(
            self.request.GET, queryset=qs
        )

        return self.filterset.qs

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Intercept standard execution if client requests PDF
        """

        if request.GET.get("pdf"):
            filtered_records: QuerySet[HireRecord] = (
                self.get_queryset()
            )

            client_name = (
                request.user.get_full_name() or request.user.username
            )

            return generate_user_inventory_pdf_response(
                user_id=request.user.pk,
                client_name=client_name,
                queryset=filtered_records,
            )

        # Default for non PDF requests.

        return super().get(request=request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # Make template context aware
        context["zone"] = "dashboard"

        # Initialise qs
        # base_qs = self.get_queryset()
        # base_qs = self.filterset.qs
        base_qs = self.object_list

        # Assign context
        context["mobile_filter"] = self.filterset
        context["desktop_filter"] = self.filterset

        # Seems redundant but needed for navbar
        context["filter"] = self.filterset

        # context["filter"] = self.filterset

        context["active_hires"] = base_qs.filter(
            returned_date__isnull=True,
            out_date__isnull=False,
        )
        context["returned_hires"] = base_qs.filter(
            returned_date__isnull=False
        )

        context["total_hires"] = base_qs.count()

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

    def handle_no_permission(self):
        """
        Custom interceptor to handle unauthenticated HTMX requests.
        """

        if self.request.headers.get("HX-Request"):
            login_url = (
                f"{reverse('account_login')}?next={self.request.path}"
            )

            response = JsonResponse(
                {
                    "error": "AUTHENTICATION_REQUIRED",
                },
                status=401,
            )
            response["HX-Redirect"] = login_url
            return response

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
                "stripePk": self.stripe_public_key,
            }
        )


class MembershipSuccessView(LoginRequiredMixin, View):
    """
    Landing checkpoint verifying completed user billing flow.
    """

    def get(self, request: HttpRequest):

        # Capture intent ID
        setup_intent_id = request.GET.get("setup_intent")
        tier_id = request.GET.get("tier_id")
        inline = request.GET.get("inline")

        membership_partial = "accounts/partials/_membership_card.html"
        status = "success"

        if setup_intent_id and not tier_id:
            try:
                intent = stripe.SetupIntent.retrieve(setup_intent_id)
                extracted_tier_id = intent.metadata.get("tier_id")
                if extracted_tier_id:
                    tier_id = int(extracted_tier_id)
            except Exception as e:
                messages.error(
                    request,
                    f"TRANSACTION_VERIFICATION_FAILED // {str(e)}",
                )
        if tier_id:
            MembershipService.provision_tier(
                request.user,
                tier_id=int(tier_id),
            )
        if inline:
            updated_tier = get_object_or_404(
                MembershipTier, pk=tier_id
            )

            html_string = render_to_string(
                membership_partial,
                {
                    "tier": updated_tier,
                    "current_tier": updated_tier,
                },
                request=request,
            )
            response = HttpResponse(
                html_string,
                status=200,
            )
            message = f"Membership updated to {updated_tier.name} successfully."

            response["HX-Trigger"] = json.dumps(
                {
                    "showToast": {
                        "message": message,
                        "status": status,
                    },
                },
            )

            return response

        if setup_intent_id:
            messages.success(
                request=request,
                message="SUCCESS // Welcome to your new membership plan.",
            )

        return redirect("accounts:membership_options")
