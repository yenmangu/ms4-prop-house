from django.shortcuts import render
from django.views import generic
from view_breadcrumbs import ListBreadcrumbMixin, DetailBreadcrumbMixin
from .models import Product
from .filters import ProductFilter


# Create your views here.
class ProductListView(
    ListBreadcrumbMixin,
    generic.ListView,
):
    model = Product
    context_object_name = "catalogue"
    template_name = "catalogue/catalogue_list.html"
    paginate_by = 12

    def get_queryset(self):

        # 1. Start with standard QuerySet, use prefetch_related to access the categories associated with CategoryJoin table
        queryset = Product.objects.all().prefetch_related("categories")

        # 2. Initialise the filter with GET params
        self.filterset = ProductFilter(
            self.request.GET,
            queryset=queryset,
        )

        # 3. Return filtered queryset
        return self.filterset.qs

        # return base_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 4. Add filterset to context
        context["filter"] = self.filterset
        return context


class ProductDetailView(DetailBreadcrumbMixin, generic.DetailView):
    model = Product
    template_name = "catalogue/catalogue_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "product"
    breadcrumb_use_pk = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context:
            print("context not found")
        return context
