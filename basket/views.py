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

            message = f"Unit '{product.name}' secured in basket."

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

        if str(basket.id) != str(current_session_basket_id):
            print(f"WARNING: Session mismatch! Mixin created {basket.id}")

        data = json.loads(request.body)
        p_id = data.get("product_id")

        line = Line.objects.filter(basket=basket, product_id=p_id).first()

        if line:
            line.delete()
            return JsonResponse(get_basket_state(basket, "Unit removed from basket"))

        # DEBUG 200 RETURN
        return JsonResponse(
            {
                "status": "error",
                "message": "Session sync lost. Item not found in active basket.",
                "debug_info": {
                    "session_basket_id": current_session_basket_id,
                    "mixin_basket_id": str(basket.id),
                },
            },
            status=200,
        )

        # DIAGNOSTIC TRACE
        print(f"\n--- DIAGNOSTIC TRACE ---")
        print(f"Request Product ID: {p_id} (Type: {type(p_id)})")
        print(f"Active Basket ID: {basket.id}")

        # Check all lines currently in this basket to see if 5 is actually there
        existing_lines = basket.lines.all()
        print(
            f"Lines in this Basket: {[f'Prod: {l.product_id} (ID: {l.id})' for l in existing_lines]}"
        )

        # Check if Product {p_id} exists at all in ANY basket (to see if session is swapped)
        all_instances = Line.objects.filter(product_id=p_id)
        print(
            f"Total instances of Product {p_id} in ANY basket: {all_instances.count()}"
        )
        if all_instances.exists():
            print(
                f"Product {p_id} belongs to Baskets: {[l.basket_id for l in all_instances]}"
            )
        print(f"------------------------\n")

        product_id = p_id
        #
        #
        if not product_id:
            return JsonResponse(
                {"status": "error", "message": f"Product with {product_id} not found"}
            )

        line = Line.objects.filter(
            basket=basket,
            product_id=product_id,
        ).first()

        if line:
            line.delete()

            return JsonResponse(
                get_basket_state(
                    basket,
                    "Unit removed from basket",
                )
            )

        return JsonResponse(
            {
                "status": "error",
                "message": "This unit is no longer in your active basket",
            },
            status=404,
        )


class BasketClearView(BasketMixin, View):

    def post(self, request, *args, **kwargs):
        basket = self.get_basket()

        # High effeciency - delete all related lines
        basket.lines.all().delete()

        return JsonResponse(get_basket_state(basket, "Basket cleared"))
