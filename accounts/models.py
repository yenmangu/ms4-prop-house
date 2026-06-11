from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.db import models

# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: django-money (https://github.com/django-money/django-money)
# Purpose: MoneyField model field wrapper for localized currency management.
# Localisation: Controls commercial pricing structures on MembershipTier.
# =========================================================================
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

    features = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="An array of feature strings.",
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
        addresses: RelatedManager["Address"]

    def __str__(self):
        return self.email


class Address(models.Model):
    """
    Represent the saved address for a customer
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    label = models.CharField(max_length=80, default="Default")
    delivery_contact_name = models.CharField(
        max_length=255, blank=True
    )
    phone_number = models.CharField(max_length=30)
    house_name_or_number = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    town_or_city = models.CharField(max_length=255)
    county = models.CharField(max_length=255)
    postcode = models.CharField(max_length=20)
    country = CountryField(default="GB")
    is_default = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
