from django.db import models
from django.utils.text import slugify
import uuid
from django.contrib.auth.models import User


# Create your models here.
class Basket(models.Model):
    """
    Stores a single Basket entity linked to a User or a Session.
    """

    class Status(models.TextChoices):
        OPEN = "op", "Open"
        MERGED = "me", "Merged"
        SAVED = "sa", "Saved"
        SUBMITTED = "su", "Submitted"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name="basket_user"
    )
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        """
        Calculates the total price of all lines within the basket.
        """
        return sum(line.line_reference for line in self.lines.all())


class Line(models.Model):
    """
    Stores a single product and its quantity within a specific Basket.
    """

    basket = models.ForeignKey(
        Basket,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        "catalogue.Product", on_delete=models.CASCADE, related_name="lines"
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    class Meta:
        unique_together = ("basket", "product")

    def __str__(self):
        """
        Returns a string representation of the line item.
        """
        return f"{self.quantity} x {self.product.title}"

    @property
    def line_references(self):
        """
        Calculates the total price for this specific line item.
        """
        return self.price_at_addition * self.quantity
