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
