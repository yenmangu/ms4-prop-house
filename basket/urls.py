from django.urls import path
from . import views

app_name = "basket"


urlpatterns = [
    path(
        "",
        views.BasketSummaryView.as_view(),
        name="summary",
    ),
    path(
        "update/",
        views.BasketUpdateView.as_view(),
        name="update",
    ),
    path(
        "nav-basket",
        views.NavBasketPartialUpdate.as_view(),
        name="nav_basket",
    ),
    path(
        "hire-form-toast/<int:product_id>/",
        views.HireFormToastView.as_view(),
        name="hire_form_toast",
    ),
]
