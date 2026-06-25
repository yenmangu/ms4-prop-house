from commerce.forms import PropHireForm
from django.contrib import messages
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views import generic

# =========================================================================
# EXTERNAL DEPENDENCY ATTRIBUTION
# Source: django-view-breadcrumbs (https://github.com/mhipszki/django-view-breadcrumbs)
# Purpose: ListBreadcrumbMixin and DetailBreadcrumbMixin generic view extensions
#          for automated page trail tracking.
# Localisation: Establishes navigational path rendering for the catalog
#               list and detail views.
# =========================================================================
from view_breadcrumbs import (
    ListBreadcrumbMixin,
    DetailBreadcrumbMixin,
)
from warehouse.services import get_stock_availability
from .models import Product
from .filters import ProductFilter
from basket.mixins import BasketMixin


# Create your views here.
@method_decorator(ensure_csrf_cookie, name="dispatch")
class ProductListView(
    BasketMixin,
    ListBreadcrumbMixin,
    generic.ListView,
):
    model = Product
    context_object_name = "catalogue"
    # Fallback for initial page load
    template_name = "catalogue/catalogue_list.html"
    paginate_by = 12

    def get_queryset(self):

        # NEW
        # Use new filter_search:
        qs = super().get_queryset().prefetch_related("categories")

        # Initialise the filters with GET params
        self.filterset = ProductFilter(
            self.request.GET,
            queryset=qs,
        )

        self.mobile_filterset = ProductFilter(
            self.request.GET,
            queryset=qs,
            mobile=True,
        )

        # Return filtered queryset
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Inject context zone
        context["zone"] = "catalogue"

        # Add filterset to context
        # context["filter"] = self.mobile_filterset

        context["mobile_filter"] = self.mobile_filterset
        context["desktop_filter"] = self.filterset

        # Seems redundant but needed for navbar
        context["filter"] = self.filterset

        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return "catalogue/partials/_product_grid.html"
        return "catalogue/catalogue_list.html"


class ProductDetailView(
    BasketMixin,
    DetailBreadcrumbMixin,
    generic.DetailView,
):
    model = Product
    template_name = "catalogue/catalogue_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "product"
    breadcrumb_use_pk = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product: Product = self.get_object()

        # Warehouse availability
        warehouse_stats = get_stock_availability(product)
        total_physical_avail = warehouse_stats["available"]

        # Basket state
        basket = self.get_basket()
        basket_line = basket.lines.filter(product=product).first()
        current_basket_qty = (
            basket_line.quantity if basket_line else 1
        )
        net_available = total_physical_avail - current_basket_qty

        # Form init
        form = PropHireForm(
            initial={
                "quantity": (
                    current_basket_qty
                    if current_basket_qty > 0
                    else 1
                ),
                "start_date": (
                    basket_line.start_date if basket_line else None
                ),
                "end_date": (
                    basket_line.end_date if basket_line else None
                ),
            }
        )

        if net_available <= 0:
            form.fields["quantity"].widget.attrs["disabled"] = True
            context["out_of_stock"] = True
        else:
            context["out_of_stock"] = False
        # Sync quantity to basket quantity and max to actual available.
        form.fields["quantity"].widget.attrs.update(
            {
                "max": max(0, net_available),
                "min": 1 if net_available > 0 else 0,
                "class": "industrial-input qty-sync-input",
            }
        )

        context["hire_form"] = form
        context["available_count"] = max(0, net_available)
        context["in_basket"] = current_basket_qty

        if not context:
            messages.ERROR(self.request, "No Context Found")
        return context
