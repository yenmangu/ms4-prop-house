from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpRequest, JsonResponse
import json
from catalogue.models import Product
from .mixins import BasketMixin
from .models import Line


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

            request.session["basket_id"] = basket.id

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

            print(f"Linking Product {product.id} to Basket {basket.id}")

            line, created = Line.objects.get_or_create(
                basket=basket,
                product=product,
                defaults={"price_at_addition": product.price},
            )

            if not created:
                line.quantity += 1
                line.save()

            return JsonResponse(
                {"status": "success", "message": f"Unit {product_id} secured in basket"}
            )

            return redirect("basket:summary")

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid JSON",
                },
                status=400,
            )
