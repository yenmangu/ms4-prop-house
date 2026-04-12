from .models import Basket
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from typing import Callable


class BasketMiddleware:
    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpRequest],
    ):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Attach a property to request to fetch basket lazily.
        Prevents unnecessary DB queries on static/media requests.
        """

        # Check for session
        if not request.session.session_key:
            request.session.create()

        # Retrieve basket
        request.basket = self.get_basket(request=request)

        response = self.get_response(request)

        return response

    def get_basket(self, request: HttpRequest) -> Basket:
        basket_id = request.session.get("basket_id")

        if basket_id:
            try:
                return Basket.objects.get(
                    id=basket_id,
                    status=Basket.Status.OPEN,
                )
            except (Basket.DoesNotExist, ValueError):
                pass

        orphan_basket = Basket.objects.filter(
            session_key=request.session.session_key,
            status=Basket.Status.OPEN,
        ).last()

        if orphan_basket:
            request.session["basket_id"] = str(orphan_basket.id)
            return orphan_basket

        basket = Basket.objects.create(
            session_key=request.session.session_key,
        )
        request.session["basket_id"] = str(basket.id)

        return basket
