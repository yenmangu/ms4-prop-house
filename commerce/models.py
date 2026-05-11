from django.db import models, transaction
from django.conf import settings
from djmoney.models.fields import MoneyField
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from accounts.models import User
    from basket.models import Basket
# Create your models here.


class Order(models.Model):
    """
    _Domain:_ Commerce / Finance
    This is the 'master' document.
    It represents the customer's legal commitment to pay,
    and PropHouse's legal commitment to provide service.

    _Real World Context:_
    This model serves the 'Accounts' and 'Management' departments.
    It is the envelope that holds the entire transaction.
    While `warehouse` cares about boxes and serial numbers,
    this model cares about the 'Who' (Customer),
    the 'How Much' (`total_price`),
    and the 'Is it paid?' (`stripe_pid`).

    _Scaling Potential:_
    By keeping this model high level, is is easy to attach future 'front office' features, such as:
    - PDF Invoice generation
    - Credit Notes
    - Customer Loyalty points

    without ever having to touch warehouse fulfillment logic.
    """

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
        items: RelatedManager["OrderItem"]

    @classmethod
    def create_from_basket(
        cls, basket: "Basket", user: "User", name: str, email: str
    ) -> "Order":
        """
        Factory method to create an Order and its items from a Basket
        Handles the new logistics pipeline for Hires
        """

        with transaction.atomic():
            order = cls.objects.create(
                user=user if user.is_authenticated else None,
                full_name=name,
                email=email,
                total_price=basket.total_price,
                stripe_pid=f"pending_{uuid.uuid4()}",
            )

            order_items = [
                OrderItem(
                    order=order,
                    # product=line.product.name,
                    product=line.product,
                    product_name=line.product.name,
                    unit_price=line.price_at_addition,
                    line_total=line.line_total,
                    quantity=line.quantity,
                    # Transfer hire data to OrderItem
                    start_date=line.start_date,
                    end_date=line.end_date,
                    production_name=line.production_name,
                )
                for line in basket.lines.all()
            ]
            OrderItem.objects.bulk_create(order_items)
        return order

    def __str__(self):
        return f"Order {self.id} [{self.get_status_display()}]"


class OrderItem(models.Model):
    """
    _Domain:_ Commerce / Sales & Billing

    The 'financial' record of a product being sold or hired.
    It tracks the commercial agreement: what was promised, at what price and in what quantity.

    _Real World Context:_
    Serves as the 'Front Office' or Sales Dpt.
    Captures the 'abstract' side of the transation (e.g., '5 units of Police Tape').
    While the warehouse cares about the specific serial numbers (physical assets),
    the sales dept cares about unit price (`unit_price`) and ensuring customer is billed correctly.

    _The Bridge:_
    This model is the parent to `warehouse.HireRecord`.
    If a customer orders 5 units, this single `OrderItem` will act as the anchor
    for 5 individual physical `HireRecord` entries.
    This separation allows money to be managed here (`commerce`), and pysical assets
    to be managed at the `warehouse` domain.

    _Data Integrity (`models.PROTECT`):_
    The `product` relation is protected. Even if `Product` entry is discontinued
    in the catalogue, the `OrderItem` is preserved as a legal record of what customer paid for
    at that specific time.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalogue.Product",
        # Prevent deleting products that are in orders.
        on_delete=models.PROTECT,
    )
    product_name = models.CharField(
        max_length=255,
        help_text="Snapshot of the product name at time of purchase",
    )

    quantity = models.PositiveIntegerField(default=1)

    # Logistical snapshot
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    production_name = models.CharField(max_length=255, blank=True)

    unit_price = MoneyField(
        max_digits=14,
        decimal_places=2,
    )
    line_total = MoneyField(
        max_digits=14,
        decimal_places=2,
    )

    if TYPE_CHECKING:
        from catalogue.models import Product

        product: Product

    def __str__(self):
        return f"{self.quantity} x {self.product_name} (Order: {self.order.pk})"
