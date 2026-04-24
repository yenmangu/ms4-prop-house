from .models import Basket
from django.http import HttpRequest
from .services import get_basket_for_request


class BasketMixin:
    """
    UPDATE:
    Uses new service layer method `get_basket_for_request`

    OLD:
    Provides utility methods to retrieve or create a basket from the session
    """

    def get_basket(self):

        request: HttpRequest = self.request

        return get_basket_for_request(request=request)

    # Deprecated in favour of above

    # request: HttpRequest = self.request

    # if not request.session.session_key:
    #     request.session.create()

    # basket_id = self.request.session.get("basket_id")

    # # NEW DEBUG LINE
    # print(f"DEBUG: Session Key being checked: {self.request.session.session_key}")
    # print(f"DEBUG: basket_id found in session: {basket_id}")

    # if basket_id:
    #     try:
    #         return Basket.objects.get(id=basket_id, status=Basket.Status.OPEN)
    #     except (Basket.DoesNotExist, ValueError):
    #         pass

    # if request.session.session_key:
    #     orphan_basket = Basket.objects.filter(
    #         session_key=request.session.session_key, status=Basket.Status.OPEN
    #     ).last()

    #     if orphan_basket:
    #         # Re-Bind the lost data
    #         request.session["basket_id"] = str(orphan_basket.id)
    #         request.session.modified = True
    #         return orphan_basket

    # return self._create_basket()

    def _create_basket(self):

        request: HttpRequest = self.request

        if not request.session.session_key:
            request.session.create()

        basket = Basket.objects.create(
            session_key=request.session.session_key,
        )

        # Ensure session save
        request.session["basket_id"] = str(basket.id)
        request.session.modified = True
        request.session.save()

        return basket
