from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse
import json
from catalogue.models import Product
from .mixins import BasketMixin
from .models import Line
from .utils import get_basket_state


# Create your views here.


class BasketSummaryView(BasketMixin, View):
    """
    Handles displaying a summary of the current basket
    """

    template_name = "basket/basket_summary.html"

    def get(self, request, *args, **kwargs):
        # DEBUG: See what the session thinks the ID is BEFORE calling the mixin
        session_id_before = request.session.get("basket_id")
        print(f"--- SUMMARY VIEW ACCESS ---")
        print(f"Session ID in Cookie: {session_id_before}")

        basket = self.get_basket()

        print(f"Final Basket ID for Render: {basket.id}")
        print(f"---------------------------")

        return render(
            request,
            "basket/basket_summary.html",
            {"basket": basket},
        )

    # def get(self, request, *args, **kwargs):
    #     basket = self.get_basket()
    #     return render(
    #         request,
    #         "basket/basket_summary.html",
    #         {
    #             "basket": basket,
    #         },
    #     )


class BasketAddView(BasketMixin, View):
    """
    Handles adding a product to user's basket
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        print("Hit post route")
        basket = self.get_basket()

        try:

            data = json.loads(request.body)
            product_id = data["product_id"]

            if not product_id:
                return JsonResponse(
                    {
                        "error": "No product_id provided",
                    },
                    status=400,
                )
            product = get_object_or_404(Product, pk=product_id)

            line, created = Line.objects.get_or_create(
                basket=basket,
                product=product,
                defaults={"price_at_addition": product.price},
            )

            if not created:
                line.quantity += 1
                line.save()

            message = f"Unit '{product.name}' secured in basket."
            return JsonResponse(get_basket_state(basket, message))

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON",
                },
                status=400,
            )
        except Exception as e:
            # Keep this for now while transitioning, then move to logging
            print(f"CRITICAL ERROR: {e}")
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Internal server error",
                },
                status=500,
            )


class BasketRemoveView(BasketMixin, View):

    def post(self, request: HttpRequest, *args, **kwargs):
        current_session_basket_id = request.session.get("basket_id")
        print(f"--- REMOVE ATTEMPT ---")
        print(f"Session Key: {request.session.session_key}")
        print(f"Basket ID stored in Session: {current_session_basket_id}")

        # This now uses the `session_key` to find the correct basket
        basket = self.get_basket()

        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")

            if not product_id:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Product ID required",
                    },
                    status=400,
                )

            line = Line.objects.filter(basket=basket, product_id=product_id).first()

            if line:
                line.delete()
                return JsonResponse(
                    get_basket_state(basket, "Unit removed"),
                )
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Item not found in basket",
                },
                status=404,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


class BasketClearView(BasketMixin, View):

    def post(self, request, *args, **kwargs):
        basket = self.get_basket()

        # High effeciency - delete all related lines
        basket.lines.all().delete()

        return JsonResponse(get_basket_state(basket, "Basket cleared"))
