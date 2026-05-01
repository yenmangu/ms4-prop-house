from django.urls import path
from . import views

app_name = "commerce"

urlpatterns = [
    path(
        "checkout-success/",
        views.CheckoutSuccessView.as_view(),
        name="checkout_success",
    ),
    path(
        "",
        views.paymentIntentView.as_view(),
        name="create_payment_intent",
    ),
]
