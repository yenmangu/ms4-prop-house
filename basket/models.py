from django.db import models, transaction
from django.utils.text import slugify
from django.http import HttpRequest
import uuid

# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: django-money (https://github.com/django-money/django-money)
# Purpose: MoneyField model field and Money utility class for precise,
#          currency-aware arithmetic operations.
# Localisation: Controls monetary calculations on basket items and line totals.
# =========================================================================
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from catalogue.models import Product
from django.conf import settings
from django.db import models
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

USER_MODEL = getattr(settings, "AUTH_USER_MODEL")


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
        USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name="basket_user",
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

    # Allows access of method if Basket not instantiated in DB yet
    @classmethod
    def handle_login_merge(cls, request: HttpRequest, user) -> None:
        """
        Refactored logic to find/merge baskets on login OR email confirmation.
        """

        guest_basket_id: Optional[str] = request.session.get(
            "basket_id"
        )

        print(
            f"DEBUG: Signal received. Session Basket ID: {guest_basket_id}"
        )

        if not guest_basket_id:
            print(
                "DEBUG: No basket ID found in session. Merging aborted."
            )
            return
        try:

            guest_basket: Basket = cls.objects.get(
                id=guest_basket_id,
                user__isnull=True,
            )

            print(
                f"DEBUG: Found Guest Basket {guest_basket.id} in DB."
            )

            user_basket: Optional[Basket] = (
                cls.objects.filter(
                    user=user,
                    status=cls.Status.OPEN,
                )
                .exclude(id=guest_basket_id)
                .first()
            )

            active_basket: Basket

            if user_basket:
                guest_basket.merge_into(user_basket)
                active_basket = user_basket
            else:
                guest_basket.user = user
                guest_basket.save()
                active_basket = guest_basket

            # Ensure UUID is cast to string for session compatibility

            request.session["basket_id"] = str(active_basket.id)

            print(
                f"DEBUG: Merge successful. Active Basket: {request.session['basket_id']}"
            )

        except cls.DoesNotExist:
            # If the guest basket ID in session doesn't exist in DB,
            # do nothing and let the next request create a fresh one.
            print(
                f"DEBUG: Basket {guest_basket_id} exists in session but NOT in DB."
            )
            pass

    def merge_into(self, target_basket: Basket):
        """
        Merge all lines from current basket to target basket.
        Each 'basket' instance is a reference to the Basket object.
        """

        if self.id == target_basket.id or self.is_empty:
            return target_basket

        # If one line fails, all fail
        with transaction.atomic():
            for line in self.lines.all():
                target_basket.update(
                    product_id=line.product.id, quantity=line.quantity
                )
            self.status = self.Status.MERGED
            self.save()
        return target_basket

    def update(
        self,
        product_id,
        action_type=Action.ADD,
        quantity=1,
        *args,
        **kwargs,
    ):
        """
        Public API for modifying basket. Accepts any number of arguments to support evolving hire data.
        Uses private _add, _remove, _clear
        methods for lower level DB function.
        """

        if action_type == self.Action.ADD:
            return self._add(
                product_id=product_id,
                quantity=quantity,
                *args,
                **kwargs,
            )
        elif action_type == self.Action.REMOVE:
            return self._remove(product_id=product_id)
        elif action_type == self.Action.CLEAR:
            return self._clear()
        else:
            raise ValueError(f"Invalid update action: {action_type}")

    def _add(self, product_id, quantity=1, *args, **kwargs):
        """
        Internal handler to add a product to the basket or increment quantity.
        Pulls specific hire data out of `**kwargs` for the `Line` model.

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

        # Safety Check: if ghost basket, save to DB.
        # Check if basket has been updated during current lifecycle

        if (
            not self._state.adding
            or not Basket.objects.filter(pk=self.pk).exists()
        ):
            print(f"DEBUG: Basket {self.pk} not in DB. Saving now.")
            self.save()

        product = Product.objects.get(id=product_id)

        defaults = {
            "price_at_addition": product.price,
        }

        # Only update logistics if they are actually provided in the request
        if kwargs.get("start_date"):
            defaults["start_date"] = kwargs.get("start_date")
        if kwargs.get("end_date"):
            defaults["end_date"] = kwargs.get("end_date")
        if kwargs.get("production_name"):
            defaults["production_name"] = kwargs.get(
                "production_name"
            )

        line, created = self.lines.update_or_create(
            product=product,
            # defaults={
            #     "price_at_addition": product.price,
            #     # Additional Hire Data
            #     "start_date": kwargs.get("start_date"),
            #     "end_date": kwargs.get("end_date"),
            #     "production_name": kwargs.get("production_name", ""),
            # },
            #
            # Use new defaults dict created above
            defaults=defaults,
        )

        if created:
            line.quantity = int(quantity)
        else:

            # Use F here to remove any race condition
            # i.e.: user adds to basket twice rapidly
            line.quantity = models.F("quantity") + int(quantity)

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
        # Safety check, almost redundant but my own peace of mind
        if self._state.adding:
            return (0, {})

        # Back to normal
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

    @property
    def is_empty(self):
        return not self.lines.exists()


class Line(models.Model):
    """
    Stores a single product and its quantity within a specific Basket.
    """

    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="basket_lines",
    )
    quantity = models.PositiveIntegerField(default=1)

    # Preliminary Hire Data
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    production_name = models.CharField(max_length=255, blank=True)

    # New 'django-money' field
    price_at_addition = MoneyField(
        max_digits=12, decimal_places=2, default_currency="GBP"
    )

    # Add class level type checking for IDE auto completion
    if TYPE_CHECKING:
        from catalogue.models import Product

        product: Product

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
