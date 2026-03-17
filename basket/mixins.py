from .models import Basket


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
                return self.get_basket()

    def _create_basket(self):
        basket = Basket.objects.create()
        self.request.session["basket_id"] = str(basket.id)
        return basket
