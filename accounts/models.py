from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models

if TYPE_CHECKING:
    from commerce.models import Order
    from django.db.models.manager import RelatedManager


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

    if TYPE_CHECKING:
        orders: RelatedManager["Order"]

    def __str__(self):
        return self.email
