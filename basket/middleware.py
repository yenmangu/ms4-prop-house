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

        # user__isnull - check for isnull property on `user` field
        if request.session.session_key:
            orphan = Basket.objects.filter(
                session_key=request.session.session_key,
                status=Basket.Status.OPEN,
                user__isnull=True,
            ).first()
            if orphan:
                request.session["basket_id"] = str(orphan.id)
                return orphan

        # Return unsaved instance (ghost basket)
        # Allows templates to call total_items without errors
        # Does not save row to DB until item is added
        return Basket(session_key=request.session.session_key)

    # Deprecated in favour of above

    # def get_basket(self, request: HttpRequest) -> Basket:
    #     basket_id = request.session.get("basket_id")

    #     if basket_id:
    #         try:
    #             return Basket.objects.get(
    #                 id=basket_id,
    #                 status=Basket.Status.OPEN,
    #             )
    #         except (Basket.DoesNotExist, ValueError):
    #             pass

    #     orphan_basket = Basket.objects.filter(
    #         session_key=request.session.session_key,
    #         status=Basket.Status.OPEN,
    #     ).last()

    #     if orphan_basket:
    #         request.session["basket_id"] = str(orphan_basket.id)
    #         return orphan_basket

    #     basket = Basket.objects.create(
    #         session_key=request.session.session_key,
    #     )
    #     request.session["basket_id"] = str(basket.id)

    #     return basket
