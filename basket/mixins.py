from .models import Basket
from django.http import HttpRequest


class BasketMixin:
    """
    Provides utility methods to retrieve or create a basket from the session
    """

    def get_basket(self):
        basket_id = self.request.session.get("basket_id")

        if basket_id:
            try:
                return Basket.objects.get(id=basket_id, status=Basket.Status.OPEN)
            except Basket.DoesNotExist:
                pass
        return self._create_basket()

    def _create_basket(self):
        basket = Basket.objects.create()
        request: HttpRequest = self.request
        request.session["basket_id"] = str(basket.id)
        request.session.modified = True
        return basket
