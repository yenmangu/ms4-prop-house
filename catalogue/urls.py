from django.urls import include, path
from .views import ProductListView

app_name = "catalogue"

urlpatterns = [
    path(
        "products/",
        ProductListView.as_view(),
        name=ProductListView.list_view_name,
    ),
]
