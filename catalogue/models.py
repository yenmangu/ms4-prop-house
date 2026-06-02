from typing import TYPE_CHECKING
from django.db import models
from django.utils.text import slugify

# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: django-money (https://github.com/django-money/django-money)
# Purpose: MoneyField model field wrapper for localized, currency-aware
#          monetary storage.
# Localisation: Establishes base inventory values on the commercial Product
#               definition.
# =========================================================================
from djmoney.models.fields import MoneyField

# Create your models here.


class CategoryProductJoin(models.Model):
    """Join table provides many-to-many relationship between Product and Category"""

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "category"],
                name="unique_product_category",
            )
        ]

    def __str__(self):
        return f"{self.product} <-> {self.category}"


class Category(models.Model):
    """
    Stores a single Category entity

    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.build_unique_slug()
        return super().save(*args, **kwargs)

    def build_unique_slug(self) -> str:
        base_slug = slugify(self.name) or "product"
        candidate_slug = base_slug
        suffix = 2

        while (
            self.__class__.objects.filter(slug=candidate_slug)
            .exclude(pk=self.pk)
            .exists()
        ):
            candidate_slug = f"{base_slug}-{suffix}"
            suffix += 1
        return candidate_slug


class Product(models.Model):
    """
    Stores a single Product entity

    Note: slug has 'blank=true' set, but will be enforced in view logic
    """

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    categories = models.ManyToManyField(
        Category,
        related_name="products",
        through=CategoryProductJoin,
    )
    price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="GBP",
    )
    discount_eligible = models.BooleanField(default=False)
    stock_quantity = models.PositiveIntegerField(default=0)
    featured_image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # New Stripe Fields
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Stripe Product ID (prod_...)",
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Stripe Price ID (price_...)",
    )

    # Type determination
    is_recurring = models.BooleanField(
        default=False,
        help_text="Check this if product is a subscription",
    )

    is_hire = models.BooleanField(default=False)

    # Administration
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        from django.db.models.manager import RelatedManager
        from warehouse.models import StockItem

        stock_items: RelatedManager["StockItem"]

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.build_unique_slug()
        return super().save(*args, **kwargs)

    def build_unique_slug(self) -> str:
        base_slug = slugify(self.name) or "product"
        candidate_slug = base_slug
        suffix = 2

        while (
            self.__class__.objects.filter(slug=candidate_slug)
            .exclude(pk=self.pk)
            .exists()
        ):
            candidate_slug = f"{base_slug}-{suffix}"
            suffix += 1
        return candidate_slug
