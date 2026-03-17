from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from catalogue.models import Product
from .mixins import BasketMixin
from .models import Line


# Create your views here.


class BasketSummaryView(BasketMixin, View):
    """
    Handles displaying a summary of the current basket
    """


class BasketAddView(BasketMixin, View):
    """
    Handles adding a product to user's basket
    """

    def post(self, request, *args, **kwargs):
        basket = self.get_basket()
        product = get_object_or_404(
            Product,
            pk=kwargs.get("pk"),
        )

        line, created = Line.objects.get_or_create(
            basket=basket,
            product=product,
            defaults={"price_at_addition": product.price},
        )

        if not created:
            line.quantity += 1
            line.save()

        return redirect("basket:summary")
