from django.db import models
from django.utils.text import slugify
from djmoney.models.fields import MoneyField
from djmoney.money import Money
import uuid
from django.contrib.auth.models import User
from catalogue.models import Product

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


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

    class Action(models.TextChoices):
        ADD = "add"
        REMOVE = "remove"
        CLEAR = "clear"

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
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
    )

    # Add class level type checking for IDE auto completion
    if TYPE_CHECKING:
        lines: RelatedManager["Line"]

    def update(self, product_id, action_type=Action.ADD, quantity=1):
        """
        Public API for modifying basket. Uses private _add, _remove, _clear
        methods for lower level DB function.
        """

        if action_type == self.Action.ADD:
            return self._add(product_id=product_id, quantity=quantity)
        elif action_type == self.Action.REMOVE:
            return self._remove(product_id=product_id)
        elif action_type == self.Action.CLEAR:
            return self._clear()
        else:
            raise ValueError(f"Invalid update action: {action_type}")

    def _add(self, product_id, quantity=1):
        """
        Internal handler to add a product to the basket or increment quantity.

        Args:
            product_id (uuid/int): The primary key of the Product to add.
            quantity (int): The amount to add. Defaults to 1.

        Returns:
            Line: The created or updated Line instance, or None if quantity < 1.

        Side Effects:
            - Performs a DB update_or_create on the Line model.
            - Updates price_at_addition based on current Product price.
            - Saves the Basket instance to update the updated_on timestamp.
        """
        if int(quantity) < 1:
            return None

        product = Product.objects.get(id=product_id)

        line, created = self.lines.update_or_create(
            product=product,
            defaults={"price_at_addition": product.price},
        )
        if created:
            line.quantity = int(quantity)
        else:

            # Use F here to remove any race condition
            # i.e.: user adds to basket twice rapidly
            line.quantity = models.F("quantity") + int(quantity)
        line.quantity = (
            (line.quantity + int(quantity)) if not created else int(quantity)
        )

        line.save()

        # Because `F() `is used, Line object doesnt have new value yet. # Must manually call `refresh_from_db()`:
        line.refresh_from_db()
        self.save()

        return line

    def _remove(self, product_id):
        """
        Internal handler to completely remove a product line from the basket.

        Args:
            product_id (uuid/int): The primary key of the Product to remove.

        Returns:
            tuple: (int, dict) The number of items deleted and a dictionary
                   with the number of deletions per object type.

        Side Effects:
            - Saves the Basket instance to update the updated_on timestamp.
        """
        result = self.lines.filter(product_id=product_id).delete()
        self.save()
        return result

    def _clear(self):
        """
        Internal handler to remove all lines from the basket.

        Side Effects:
            - Deletes all related Line objects.
            - Saves the Basket instance to update the updated_on timestamp.
        """
        self.lines.all().delete()
        self.save()

    @property
    def total_price(self):
        """
        Calculates the total price of all lines within the basket.
        Returns a Money object for precise arithmetic.
        """
        # Start with zero money in correct currency
        total = Money(0, "GBP")
        for line in self.lines.all():
            total += line.line_total
        return total

        # Deprecated in favour of above
        # return sum(line.line_reference for line in self.lines.all())

    @property
    def total_items(self):
        """
        Return total quantity of all items in the basket
        """
        return sum(line.quantity for line in self.lines.all())


class Line(models.Model):
    """
    Stores a single product and its quantity within a specific Basket.
    """

    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(
        "catalogue.Product", on_delete=models.CASCADE, related_name="basket_lines"
    )
    quantity = models.PositiveIntegerField(default=1)

    # New 'django-money' field
    price_at_addition = MoneyField(
        max_digits=12, decimal_places=2, default_currency="GBP"
    )

    # Deprecated in favour of above
    # price_at_addition = models.DecimalField(
    #     max_digits=12,
    #     decimal_places=2,
    # )

    class Meta:
        unique_together = ("basket", "product")

    def __str__(self):
        """
        Returns a string representation of the line item.
        """
        return f"{self.quantity} x {self.product.title}"

    @property
    def line_total(self):
        """
        Renamed from line_reference for clarity.
        Calculates the price * quantity of this specific line item.
        """
        return self.price_at_addition * self.quantity
