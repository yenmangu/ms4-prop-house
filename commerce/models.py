from django.db import models
from django.conf import settings
from djmoney.models.fields import MoneyField
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

# Create your models here.


class Order(models.Model):

    class OrderStatus(models.TextChoices):
        PENDING = "PE", "Pending"
        PROCESSING = "PR", "Processing"
        PAID = "PA", "Paid"
        FAILED = "FA", "Failed"
        CANCELLED = "CA", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Tracking
    full_name = models.CharField(max_length=255)
    email = models.EmailField()

    # Stripe
    stripe_pid = models.CharField(
        max_length=255,
        unique=True,
    )
    status = models.CharField(
        max_length=2,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )

    total_price = MoneyField(max_digits=14, decimal_places=2, default_currency="GBP")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Allow class level type checking for IDE auto completion
    if TYPE_CHECKING:
        lines: RelatedManager["OrderLine"]

    def __str__(self):
        return f"Order {self.id} [{self.get_status_display()}]"


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="lines",
        on_delete=models.CASCADE,
    )
    product_name = models.CharField(max_length=255)
    price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency="GBP",
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
