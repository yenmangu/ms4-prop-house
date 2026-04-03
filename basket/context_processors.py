from django.http import HttpRequest
from .models import Basket


def basket_context(request: HttpRequest):
    """
    Makes basket object globally available in all templates
    """

    basket = None

    # Check authenticated user first (highest priority)
    if request.user.is_authenticated:

        # Get most recent active basket
        basket = Basket.objects.filter(user=request.user, status="active").first()

    if not basket:
        basket_id = request.session.get("basket_id")
        if basket_id:

            # Fallback to session for guests
            try:
                basket = Basket.objects.get(
                    id=basket_id,
                    status="axctive",
                )

            except Basket.DoesNotExist:
                # Clean up stale session ID if the basket was deleted/expired
                del request.session["basket_id"]

    return {
        "global_basket": None,
        "basket_count": basket.total_items if basket else 0,
    }
