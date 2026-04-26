import stripe

from django.conf import settings
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from basket.models import Basket

STRIPE_CONFIG = getattr(settings, "STRIPE_KEYS", {})
stripe_api_key = STRIPE_CONFIG.get("stripe_sk")


class PaymentService:

    @staticmethod
    def create_payment_intent(basket: Basket):
        """
        Creates the Stripe PaymentIntent based on the basket total
        """

        try:
            # Using Money so use total_price.amount to extract value
            total_amount = basket.total_price.amount
            # Stripe expects integers in the smallest currency unit (e.g., 1000 = £10.00)

            amount_in_Pence = int(
                (total_amount * Decimal("100")).quantize(Decimal("1"))
            )

            currency = str(basket.total_price.currency).lower()

            intent = stripe.PaymentIntent.create(
                amount=amount_in_Pence,
                currency=currency,
                metadata={
                    "basket_id": str(basket.id),
                    "user_id": basket.user.id if basket.user else "anonymous",
                },
                automatic_payment_methods={"enabled": True},
            )

            return intent.client_secret, None
        except Exception as e:
            return None, str
