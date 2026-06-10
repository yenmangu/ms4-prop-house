from django.contrib import messages
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.loader import render_to_string
import json
from catalogue.models import Product
from django.views.generic import TemplateView
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
        # DEBUG: Uncomment when investigating basket session resolution -
        # See what the session thinks the ID is BEFORE calling the mixin
        # Uncomment below:
        # session_id_before = request.session.get("basket_id")
        # print(f"--- SUMMARY VIEW ACCESS ---")
        # print(f"Session ID in Cookie: {session_id_before}")

        basket = self.get_basket()

        # DEBUG: Uncomment for debug
        # print(f"Final Basket ID for Render: {basket.id}")
        # print(f"---------------------------")

        return render(
            request,
            "basket/basket_summary.html",
            {"basket": basket},
        )


class BasketAddView(BasketMixin, View):
    """
    Handles adding a product to user's basket
    """

    def post(self, request: HttpRequest, *args, **kwargs):
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

        # DEBUG: Uncomment to debug basket issues
        # print(f"--- REMOVE ATTEMPT ---")
        # print(f"Session Key: {request.session.session_key}")
        # print(
        #     f"Basket ID stored in Session: {current_session_basket_id}"
        # )

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

            line = Line.objects.filter(
                basket=basket, product_id=product_id
            ).first()

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

        return JsonResponse(
            get_basket_state(basket, "Basket cleared")
        )


class BasketUpdateView(BasketMixin, View):
    """
    BasketUpdateView handles all basket modfiications.
    Previously split across multiple views; this consolidation
    allows all update logic to be centralised.

    Args:
        BasketMixin: _description_
        View: _description_
    """

    def post(self, request: HttpRequest, *args, **kwargs):
        message = "Basket updated successfullty"
        status = "success"

        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            action = data.get("action")
            quantity = data.get("quantity", 1)
            # Additional hire data - will NOT fail if missing values
            # i.e., if added from summary view
            hire_context = {
                "start_date": data.get("start_date"),
                "end_date": data.get("end_date"),
                "production_name": data.get("production_name", ""),
            }

            basket = self.get_basket()
            # basket = getattr(request, "basket", None)

            request.session["basket_id"] = str(basket.id)
            request.session.modified = True

            # Call the update
            basket.update(
                product_id=product_id,
                action_type=action,
                quantity=quantity,
                # Additional hire context supported by `**kwargs`
                **hire_context,
            )

            # Dynamic messaging

            messages_map = {
                "ADD": "Item added to basket",
                "REMOVE": "Item removed from basket",
                "CLEAR": "Basket cleared",
            }

            message = messages_map.get(action.upper())

            # Added HTMX logic
            if request.headers.get("HX-Request"):
                html = render_to_string(
                    "basket/partials/_basket_update_response.html",
                    {
                        "basket": basket,
                    },
                    request=request,
                )

                # Status 200 by default, but included for brevity
                response = HttpResponse(
                    html,
                    status=200,
                )

                response["HX-Trigger"] = json.dumps(
                    {
                        "showToast": {
                            "message": message,
                            "status": status,
                        },
                    }
                )

                return response

            # Fallback for non-HTMX
            return redirect("basket:summary")

            # Deprecated in favour of new HTMX method above
            return JsonResponse(
                get_basket_state(
                    basket,
                    message=message,
                    status=status,
                )
            )
        except Exception as e:
            return JsonResponse(
                get_basket_state(
                    basket=None,
                    message=f"Update failed: {str(e)}",
                    status="danger",
                ),
                status=400,
            )


class NavBasketPartialUpdate(BasketMixin, TemplateView):
    template_name = "basket/partials/_nav_basket_logic.html"

    def get_context_data(self, **kwargs):
        """
        Add basket to context
        """

        context = super().get_context_data(**kwargs)
        context["basket"] = self.get_basket()
        return context
