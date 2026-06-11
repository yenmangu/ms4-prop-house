from typing import Optional
from accounts.forms import CustomerAddressForm
from accounts.models import User
from accounts.services import MembershipService
from commerce.services import CheckoutService
from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View, generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .mixins import StripeMixin
from basket.mixins import BasketMixin
from .models import Order, OrderItem
from .utils import fulfill_order
from basket.models import Basket
from accounts.models import User
import stripe
import uuid

# Create your views here.


class CheckoutDetailsView(BasketMixin, generic.TemplateView):
    """
    Serves initial form via HTMX
    """

    template_name = "commerce/includes/_customer_details_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request: HttpRequest = self.request
        default_address = None
        user = request.user

        if request.user.is_authenticated and isinstance(user, User):
            default_address = user.addresses.filter(
                is_default=True
            ).first()

        context["address_form"] = CustomerAddressForm()
        context["default_address"] = default_address

        if default_address:
            context["default_address_payload"] = {
                "deliveryContactName": default_address.delivery_contact_name,
                "phoneNumber": default_address.phone_number,
                "houseNameOrNumber": default_address.house_name_or_number,
                "addressLine1": default_address.address_line_1,
                "addressLine2": default_address.address_line_2,
                "townOrCity": default_address.town_or_city,
                "county": default_address.county,
                "postcode": default_address.postcode,
                "country": str(default_address.country),
            }

        return context


class paymentIntentView(StripeMixin, BasketMixin, View):
    """
    Handles Stripe Payment Intent creation.
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        basket: Optional["Basket"] = self.get_basket()
        if not basket or basket.is_empty:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Empty Basket",
                },
                status=400,
            )

        # Use service for heavy lifting
        intent, error = (
            CheckoutService.create_payment_intent_for_basket(
                basket=basket,
                user=request.user,
                post_data=request.POST,
            )
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
            },
        )


class CheckoutSuccessView(
    StripeMixin, BasketMixin, generic.TemplateView
):
    template_name = "commerce/checkout-success.html"

    def get(self, request, *args, **kwargs):
        """
        get Overrides the standard `get` method, to trigger the HTMX front end.
        Calls the `super().get(...)` method to maintain existing pipeline.
        """
        response = super().get(request=request, *args, **kwargs)
        response["HX-Trigger"] = "basketUpdated"
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Now stripe_pid is linked to Order model, no longer checking client_secret
        # client_secret = self.request.GET.get("payment_intent_client_secret")

        intent_id = self.request.GET.get("payment_intent")

        if intent_id:
            try:
                # Verify directly from Stripe servers
                intent = stripe.PaymentIntent.retrieve(intent_id)

                context["payment_intent"] = intent
                if intent.status == "succeeded":

                    # Use utility to fulfill order
                    basket = self.get_basket()
                    fulfill_order(
                        intent_id, basket.id if basket else None
                    )

            except stripe.error.StripeError as e:
                context["error"] = str(e)

        return context


@csrf_exempt
@require_POST
def stripe_webhook(request: HttpRequest):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WH_SECRET,
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Convert Stripe's custom object to Python dict
    event_data = event.data.object._to_dict_recursive()

    # Updated: Existing retail order
    if event.type == "payment_intent.succeeded":
        # intent = event.data.object
        intent_id = event_data.get("id")

        metadata = event_data.get("metadata", {}) or {}
        basket_id = metadata.get("basket_id")

        if basket_id:
            try:
                # Rebuild basket from ID stored in stripe
                basket = Basket.objects.get(id=basket_id)
            except Basket.DoesNotExist:
                pass

            # Keep safe from mock data crashes
            try:
                fulfill_order(intent_id, basket_id=basket_id)
            except Exception:
                pass

    # Updated: New Subscription handling
    elif event.type == "checkout.session.completed":
        session = event.data.object

        # Check if spawned as subscription
        # Safe dictionary lookups! (stressful to work this one out)
        if event_data.get("mode") == "subscription":
            metadata = event_data.get("metadata", {})
            metadata = getattr(session, "metadata", {})

            user_id = metadata.get("user_id")
            tier_id = metadata.get("tier_id")

            if user_id and tier_id:
                try:
                    user = User.objects.get(pk=user_id)
                    MembershipService.provision_tier(
                        user=user,
                        tier_id=int(tier_id),
                    )
                except ValueError:
                    # If mock values cannot be cast to int
                    pass
                except User.DoesNotExist:
                    # Handle errors retrieving User account

                    pass

    # Subscription expires or cancelled
    elif event.type == "customer.subscription.deleted":
        pass
    # Recurring billing charge fail
    elif event.type == "invoice.payment_failed":
        pass

    return HttpResponse(status=200)
