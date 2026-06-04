from django.http import HttpRequest
from .models import Basket
from typing import Dict, Any, Optional


def basket_context(request: HttpRequest):
    """
    Makes basket object globally available in all templates.
    Latest version is heavily optimised as db work offloaded to middleware.
    """

    # Check if navigating to admin
    if request.path.startswith("/admin/"):
        return {}

    basket: Optional[Basket] = getattr(request, "basket", None)

    return {
        "basket": basket,
        "basket_count": basket.total_items if basket else 0,
    }
