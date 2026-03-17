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
        "add/<int:pk>/",
        views.BasketAddView.as_view(),
        name="add",
    ),
]
