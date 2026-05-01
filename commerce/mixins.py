import stripe
from django.http import HttpRequest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class StripeMixin:
    """
    Provides methods for initialising stripe API key etc
    """

    def __init__(self, *args, **kwargs):
        stripe_keys = getattr(settings, "STRIPE_KEYS", None)

        if not stripe_keys or "stripe_sk" not in stripe_keys:
            raise ImproperlyConfigured(
                "STRIPE_KEYS['stripe_sk'] is missing in settings"
            )

        stripe.api_key = stripe_keys["stripe_sk"]

        self.stripe_public_key = stripe_keys.get("stripe_pk")

    def get_stripe_keys(self):
        """
        Returns a disctionary of the public and secret Stripe Keys
        """
        return {
            "public": self.stripe_public_key,
            "secret": stripe.api_key,
        }
