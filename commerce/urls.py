from django.urls import path
from . import views

app_name = "commerce"

urlpatterns = [
    path(
        "checkout-details/",
        views.CheckoutDetailsView.as_view(),
        name="checkout_details",
    ),
    path(
        "checkout-success/",
        views.CheckoutSuccessView.as_view(),
        name="checkout_success",
    ),
    path("webhook/", views.stripe_webhook, name="stripe_webhook"),
    path(
        "",
        views.paymentIntentView.as_view(),
        name="create_payment_intent",
    ),
]
