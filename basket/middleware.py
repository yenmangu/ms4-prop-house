from .models import Basket
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from typing import Callable
from .services import get_basket_for_request


class BasketMiddleware:
    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpRequest],
    ):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        UPDATE: Uses new unified service layer method `get_basket_for_request`

        OLD:
        Attach a property to request to fetch basket lazily.
        Prevents unnecessary DB queries on static/media requests.
        """

        request.basket = get_basket_for_request(request=request)
        return self.get_response(request)

    # New get_basket logic
    def get_basket(self, request: HttpRequest):
        """
        Logic to retrieve or associate a basket.
        Note: New method will avoid `create()` to keep it 'lazy'
        """

        if request.user.is_authenticated:
            basket, created = Basket.objects.get_or_create(
                user=request.user, status=Basket.Status.OPEN
            )
            return basket

        basket_id = request.session.get("basket_id")
        if basket_id:
            basket = Basket.objects.filter(
                id=basket_id, status=Basket.Status.OPEN
            ).first()

            if basket:
                return basket

        # Orphaned/Session key lookup (failsafe)
        orphan = Basket.objects.filter(
            session_key=request.session.session_key,
            status=Basket.Status.OPEN,
            user__isnull=True,
        ).first()

        if orphan:
            return orphan

        return Basket(
            session_Key=request.session.session_key,
        )
