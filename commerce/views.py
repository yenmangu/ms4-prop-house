from typing import Optional
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
import stripe
import uuid

# Create your views here.


class CheckoutDetailsView(BasketMixin, generic.TemplateView):
    """
    Serves initial form via HTMX
    """

    template_name = "commerce/includes/_customer_details_form.html"


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
        intent, error = CheckoutService.create_payment_intent_for_basket(
            basket=basket, user=request.user, post_data=request.POST
        )

        if error:
            return JsonResponse(
                {
                    "error": error,
                },
                status=400,
            )

        return JsonResponse(
            {
                "clientSecret": intent.client_secret,
                "stripePk": self.stripe_public_key,
            },
        )

        # TODO: Remove depprecated below
        # Below is now deprecated as service does heavy lifting

        # total = basket.total_price

        # with transaction.atomic():

        #     # Create Order object
        #     # stripe_pid uses uuid.uuid4() to create a temp placeholder, because field is mandatory

        #     order = Order.objects.create(
        #         user=request.user if request.user.is_authenticated else None,
        #         full_name=request.POST.get("name", "untitled"),
        #         email=request.POST.get("email", "email@email.com"),
        #         total_price=total,
        #         stripe_pid="pending_ref_" + str(uuid.uuid4()),
        #     )

        #     for basket_line in basket.lines.all():
        #         OrderItem.objects.create(
        #             order=order,
        #             product=basket_line.product,
        #             product_name=basket_line.product.name,
        #             unit_price=basket_line.price_at_addition,
        #             line_total=basket_line.line_total,
        #             quantity=basket_line.quantity,
        #         )

        #     # Needed for stripe
        #     total_small_units = int(total.amount * 100)

        # try:
        #     intent = stripe.PaymentIntent.create(
        #         amount=total_small_units,
        #         currency="gbp",
        #         metadata={"basket_id": basket.id, "order_id": order.id},
        #     )
        #     order.stripe_pid = intent.id
        #     order.save()

        #     return JsonResponse(
        #         {
        #             "clientSecret": intent.client_secret,
        #             "stripePk": self.stripe_public_key,
        #         },
        #     )

        # except stripe.error.StripeError as e:
        #     return JsonResponse({"error": str(e)}, status=400)


class CheckoutSuccessView(StripeMixin, BasketMixin, generic.TemplateView):
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
                    fulfill_order(intent_id, basket.id if basket else None)

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

    if event.type == "payment_intent.succeeded":
        intent = event.data.object
        intent_id = intent.id

        metadata = intent.get("metadata", {})
        basket_id = metadata.get("basket_id")

        if basket_id:
            try:
                # Rebuild basket from ID stored in stripe
                basket = Basket.objects.get(id=basket_id)
            except Basket.DoesNotExist:
                pass

        fulfill_order(intent_id, basket_id=basket_id)
