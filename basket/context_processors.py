from django.http import HttpRequest
from .models import Basket
from typing import Dict, Any, Optional


def basket_context(request: HttpRequest):
    """
    Makes basket object globally available in all templates
    """

    # Check if navigating to admin

    if request.path.startswith("/admin/"):
        return {}

    basket: Optional[Basket] = None

    # Check authenticated user first (highest priority)
    if request.user.is_authenticated:

        # Get most recent active basket
        basket = Basket.objects.filter(
            user=request.user, status=Basket.Status.OPEN
        ).first()

        if basket:
            request.session["basket_id"] = str(basket.id)

            return {
                "basket": basket,
                "basket_count": basket.total_items if basket else 0,
            }

    else:
        basket_id = request.session.get("basket_id")
        if basket_id:
            try:
                basket = Basket.objects.get(id=basket_id, status=Basket.Status.OPEN)
            except (Basket.DoesNotExist, ValueError):
                if "basket_id" in request.session:
                    del request.session["basket_id"]
                    basket = None

    # Sync session if guest basket found
    if basket and request.session.get("basket_id") != str(basket.id):
        request.session["basket_id"] = str(basket.id)

    # TODO: Remove deprecated
    # if not basket:
    #     basket_id = request.session.get("basket_id")
    #     if basket_id:

    #         # Fallback to session for guests
    #         try:
    #             basket = Basket.objects.get(
    #                 id=basket_id,
    #                 status=Basket.Status.OPEN,
    #             )

    #         except (Basket.DoesNotExist, ValueError):
    #             # Clean up stale session ID if the basket was deleted/expired
    #             if "basket_id" in request.session:
    #                 del request.session["basket_id"]
    # if basket:
    #     request.session["basket_id"] = str(basket.id)
    return {
        "basket": basket,
        "basket_count": basket.total_items if basket else 0,
    }
