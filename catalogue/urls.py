from django.urls import include, path
from .views import ProductListView, ProductDetailView

app_name = "catalogue"

urlpatterns = [
    path(
        "products/",
        ProductListView.as_view(),
        name=ProductListView.list_view_name,
    ),
    path(
        "products/<slug:slug>/",
        ProductDetailView.as_view(),
        name=ProductDetailView.detail_view_name,
    ),
]
