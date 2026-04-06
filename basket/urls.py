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
        "add/",
        views.BasketAddView.as_view(),
        name="add",
    ),
    path(
        "remove/",
        views.BasketRemoveView.as_view(),
        name="remove",
    ),
    path(
        "clear/",
        views.BasketClearView.as_view(),
        name="clear",
    ),
]
