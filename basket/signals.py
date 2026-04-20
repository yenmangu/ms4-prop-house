from typing import Any, TYPE_CHECKING
from django.db import models
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.dispatch import receiver

try:
    from allauth.account.signals import email_confirmed
except ImportError:
    # Fallback in case allauth does not import
    email_confirmed = None
from .models import Basket

if TYPE_CHECKING:
    from allauth.account.models import EmailAddress


@receiver(user_logged_in)
def merge_basket_on_login(sender, request: HttpRequest, user, **kwargs):
    """
    When a User logs in, call method om basket model
    """
    Basket.handle_login_merge(request, user)


if email_confirmed:

    @receiver(email_confirmed)
    def merge_on_email_confirmation(
        sender, request: HttpRequest, email_address: "EmailAddress", **kwargs
    ):
        """
        Triggered when allauth received email confirmation
        """
        Basket.handle_login_merge(request, email_address.user)
