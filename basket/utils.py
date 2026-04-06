from django.conf import settings
from decimal import Decimal
from typing import Any, Dict, TYPE_CHECKING
from moneyed import Money
from moneyed.l10n import format_money
from django.db.models import Model

# This block is invisible to the interpreter at runtime,
# never causes circular import crash.
if TYPE_CHECKING:
    from .models import Basket


def format_price(amount: Any) -> str:
    """
    Standardises currency formatting for the basket app.
    Uses py-money localisation for format the Money object.
    if `amount` is not already a Money oject, it converts to GBP.
    """

    if not isinstance(amount, Money):
        # Using `or 0` to ensure `None` is not accidentally passed to the Money constructor.
        amount = Money(amount=amount or 0, currency="GBP")

    return format_money(amount, locale="en_GB")


def get_basket_state(
    basket: "Basket", message: str, status: str = "success"
) -> Dict[str, Any]:
    """
    Single source of truth for the API contract.

    _Notes_
    - Even though `TYPE_CHECKING` enabled, keep `"Basket"` as a string literal to avoid a `NameError` at runtime.
    """

    # Ensure we have a valid total (handle empty basket case)
    total = basket.total_price if basket else Money(0, currency="GBP")
    items = basket.total_items if basket else 0

    return {
        "status": status,
        "message": message,
        "total_items": int(items),
        "total_price": format_price(total),
        "is_empty": bool(items == 0),
    }
