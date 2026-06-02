from django.conf import settings
from decimal import Decimal
from typing import Any, Dict, Optional, TYPE_CHECKING

# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: py-moneyed (https://github.com/py-moneyed/py-moneyed)
# Purpose: Money class validation and localized currency formatting utilities
#          (format_money).
# Localisation: Standardises international currency layout formats across the
#               application's user-facing response state.
# =========================================================================
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
    basket: Optional["Basket"],
    message: str,
    status: str = "success",
) -> Dict[str, Any]:
    """
    Single source of truth for the API contract.

    _Notes_
    - Even though `TYPE_CHECKING` enabled, keep `"Basket"` as a string literal to avoid a `NameError` at runtime.
    """

    if basket:
        items = basket.total_items
        total = basket.total_price
        is_empty = basket.is_empty

    else:
        items = 0
        total = Money(0, currency="GBP")
        is_empty = True

    return {
        "status": status,
        "message": message,
        "total_items": int(items if not is_empty else 0),
        "total_price": format_price(total),
        "is_empty": is_empty,
    }
