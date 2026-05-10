from accounts.models import User
from commerce.models import Order
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


class CheckoutService:
    """
    Orchestrates transition from a Basket to a Paid Order
    """

    @staticmethod
    def create_payment_intent_for_basket(basket: Basket, user: "User", post_data):
        """
        Orchestrates:
        1. Order Creation via Model Classmethod
        2. Stripe Interaction
        3. Order Update
        """

        # 1. Delegation to Model
        order = Order.create_from_basket(
            basket=basket,
            user=user,
            name=post_data.get("name", "untitled"),
            email=post_data.get("email", "email@email.com"),
        )

        try:
            # 2. Interact with Stripe

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

            # 3. Update Order with real PID
            order.stripe_pid = intent.id
            order.save()

            return intent, None

        except stripe.error.StripeError as e:
            # If stripe fails, order record is marked pending,
            # which can be audited later
            return None, str(e)
