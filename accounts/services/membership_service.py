from typing import Optional, Tuple

from accounts.models import MembershipTier, User
import stripe


class MembershipService:

    @staticmethod
    def create_subscription_intent(
        user: User,
        tier: MembershipTier,
    ) -> Tuple[
        Optional[stripe.SetupIntent],
        Optional[str],
    ]:
        """
        Prepares a SetupIntent for saving a Membership tier to a customer profile.
        Recurring subscription charging via Elements inside Toast UI
        """

        if not tier.stripe_price_id:
            return (
                None,
                "The membership tier does not have a valid stripe price ID associated with it.",
            )

        try:
            # Ensure customer exists in Stripe
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    metadata={"user_id": str(user.id)},
                )
                user.stripe_customer_id = customer.id
                user.save(update_fields=["stripe_customer_id"])

            intent = stripe.SetupIntent.create(
                customer=user.stripe_customer_id,
                payment_method_types=["card"],
                metadata={
                    "user_id": str(user.pk),
                    "tier_id": str(tier.pk),
                    "stripe_price_id": tier.stripe_price_id,
                },
            )
            return intent, None

        except stripe.error.StripeError as e:
            return None, str(e)

    @staticmethod
    def create_checkout_session(
        user: User,
        tier: MembershipTier,
        success_url: str,
        cancel_url: str,
    ) -> Tuple[Optional[stripe.checkout.Session], Optional[str]]:
        """
        Orchestrates Stripe Customer creation
        and initiates a Subscription Checkout Session.
        Returns tuple of (stripe_session, error_message)
        """
        if not tier.stripe_price_id:
            return (
                None,
                "The membership tier does not have a valid stripe price ID associated with it.",
            )

        try:
            # Ensure customer exists in Stripe
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}".strip()
                    or user.username,
                    metadata={"user_id": str(user.id)},
                )
                user.stripe_customer_id = customer.id
                user.save(update_fields=["stripe_customer_id"])

            # Build interactive subscription billing lifecyle session

            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[
                    {"price": tier.stripe_price_id, "quantity": 1}
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(user.pk),
                    "tier_id": str(tier.pk),
                },
            )
            return session, None
        except stripe.error.StripeError as e:
            return None, str(e)

    @staticmethod
    def provision_tier(
        user: User,
        tier_id: int,
    ) -> bool:
        """
        Transition user's active tier status.
        Usually executed upon verified payment intent completion.
        """
        try:
            tier = MembershipTier.objects.get(pk=tier_id)
            user.membership_tier = tier
            user.save(update_fields=["membership_tier"])
            return True
        except MembershipTier.DoesNotExist:
            return False
