# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: Stripe SDK (https://github.com/stripe/stripe-python)
# Purpose: Core payment gateway integration wrapper.
# Localisation: Controls payment runtime state and key initialisation.
# =========================================================================
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

        # =========================================================================
        # EXTERNAL DEPENDENCY ATTRIBUTION
        # Method: stripe.api_key
        # Purpose: Configures the third-party client instance with private credentials
        #          to enable secure server-to-server transaction requests.
        # =========================================================================
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
