from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_POST
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

    def get(self, request, *args, **kwargs):
        basket = self.get_basket()
        return render(
            request,
            "basket/basket_summary.html",
            {
                "basket": basket,
            },
        )


class BasketAddView(BasketMixin, View):
    """
    Handles adding a product to user's basket
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        print("Hit post route")
        basket = self.get_basket()

        if not basket.id:
            basket.save()
            request.session["basket_id"] = str(basket.id)

        try:

            data = json.loads(request.body)
            product_id = data["product_id"]

            if product_id:
                print(f"product_id: {product_id}")

            # Safeguard against missing product_id
            if not product_id:
                return JsonResponse(
                    {
                        "error": "No product_id provided",
                    },
                    status=400,
                )

            product = get_object_or_404(
                Product,
                pk=product_id,
            )

            # Debug message
            print(f"Linking Product {product.id} to Basket {basket.id}")

            line, created = Line.objects.get_or_create(
                basket=basket,
                product=product,
                defaults={"price_at_addition": product.price},
            )

            if not created:
                line.quantity += 1
                line.save()

            message = f"Unit '{product.title}' secured in basket."

            return JsonResponse(get_basket_state(basket, message))

        # Deprecated in favour of above
        # return JsonResponse(
        #     {
        #         "status": "success",
        #         "message": f"Unit {product_id} secured in basket",
        #         "total_items": basket.total_items,
        #         "total_price": str(basket.total_price()),
        #     }
        # )

        # Deprecated in favour of above
        # return redirect("basket:summary")

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON",
                },
                status=400,
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Internal server error",
                },
                status=500,
            )


class BasketRemoveView(BasketMixin, View):

    def post(self, request: HttpRequest, *args, **kwargs):
        basket = self.get_basket()
        data = json.loads(request.body)
        product_id = data.get("product_id")

        if product_id:
            # We filter by both basket and productn to ensure
            # users can only delete from THEIR own basket
            line = get_object_or_404(Line, basket=basket, product_id=product_id)

            line.delete()

            return JsonResponse(get_basket_state(basket, "Unit de-registered"))

        return JsonResponse(
            {
                "error": "No unit ID provided",
            },
            status=400,
        )


class BasketClearView(BasketMixin, View):

    def post(self, request, *args, **kwargs):
        basket = self.get_basket()

        # High effeciency - delete all related lines
        basket.lines.all().delete()

        return JsonResponse(get_basket_state(basket, "Basket cleared"))
