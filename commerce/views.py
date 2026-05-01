from typing import Optional
from django.shortcuts import render
from django.views import View, generic
from django.http import JsonResponse
from .mixins import StripeMixin
from basket.mixins import BasketMixin

from basket.models import Basket
import stripe

# Create your views here.


class paymentIntentView(StripeMixin, BasketMixin, View):
    """
    Handles Stripe Payment Intent creation.
    """

    def post(self, *args, **kwargs):
        basket: Optional["Basket"] = self.get_basket()
        if basket.is_empty:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Empty Basket",
                },
                status=400,
            )

        try:

            intent = stripe.PaymentIntent.create(
                amount=int(basket.total_price.amount * 100),
                currency="gbp",
                metadata={
                    "basket_id": basket.id,
                },
            )

            return JsonResponse(
                {
                    "clientSecret": intent.client_secret,
                    "stripePk": self.stripe_public_key,
                },
            )

        except stripe.error.StripeError as e:
            return JsonResponse({"error": str(e)}, status=400)


class CheckoutSuccessView(StripeMixin, BasketMixin, generic.TemplateView):
    template_name = "commerce/checkout-success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_secret = self.request.GET.get("payment_intent_client_secret")

        if client_secret:
            try:
                intent = stripe.PaymentIntent.retrieve(
                    self.request.GET.get("payment_intent"),
                )
                context["payment_intent"] = intent
                if intent.status == "succeeded":
                    # Finalise order
                    basket = self.get_basket()
                    basket.lines.all().delete()
            except stripe.error.StripeError as e:
                context["error"] = str(e)

        return context
