from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models
from djmoney.models.fields import MoneyField

if TYPE_CHECKING:
    from commerce.models import Order
    from django.db.models.manager import RelatedManager


class MembershipTier(models.Model):
    """
    Stored membership options (e.g., "Indie", "Content Creator", "Production House"), along with their commercial pricing and rental discount structures.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="The tier name (e.g., 'Indie', 'Content Creator', 'Production House')",
    )

    price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        default_currency="GBP",
        help_text="The recurring monthly price of this membership tier.",
    )

    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="The Stripe Price API ID, for recurring subscription billing.",
    )

    discount_percentage = models.PositiveIntegerField(
        default=0,
        help_text="The percentage discount applied to the basket total (e.g., 15 for 15% off)",
    )

    class Meta:
        verbose_name = "Membership Tier"
        verbose_name_plural = "Membership Tiers"
        ordering = ["price"]

        def __str__(self):
            return f"{self.name} ({self.discount_percentage}% Off)"


class User(AbstractUser):
    """
    Custom User model for Prop House.
    stripe_customer_id matches the 'User' table in the ERD
    """

    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
    )

    membership_tier = models.ForeignKey(
        MembershipTier,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
        help_text="The active membership profile associated with this user account",
    )

    if TYPE_CHECKING:
        orders: RelatedManager["Order"]

    def __str__(self):
        return self.email
