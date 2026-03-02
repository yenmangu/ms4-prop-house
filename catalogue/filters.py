import django_filters as df
from django.db.models import Q, Count
from django import forms
from .models import Product, Category


class ProductFilter(df.FilterSet):
    name = df.CharFilter(field_name="name", lookup_expr="icontains")

    categories = df.ModelMultipleChoiceFilter(
        queryset=Category.objects.order_by("name"),
        method="filter_category_and",
    )

    def filter_category_and(self, queryset, name, selected_categories):
        """
        Apply AND-based subject filtering to the queryset.

        When multiple categories are selected, only products associated with
        *all* selected categories are returned. This differs from the default
        OR behaviour provided by ModelMultipleChoiceFilter.

        This method conforms to the django-filter method-based filter
        signature: (self, queryset, name, value) -> QuerySet.

        Args:
            queryset (QuerySet): The current Product queryset being filtered.
            name (str): The name of the filter field invoking this method.
            selected_categories (QuerySet[Subject]): The validated set of
                Category instances selected by the user.

        Returns:
            QuerySet: A queryset of Product objects that include all
            selected categories.
        """
        if not selected_categories:
            return queryset

        selected_categories_ids = [category.id for category in selected_categories]

        selected_count = len(selected_categories_ids)

        # 1) Keep products that have at least the selected categories
        # 2) Count how many of the selected categories each product matches
        # 3) Only keep products where the match count equals number selected

        return queryset.filter(categories__in=selected_categories_ids).annotate(
            matched_category_count=Count(
                "categories",
                filter=Q(categories__in=selected_categories_ids),
                distinct=True,
            ).filter(matched_category_count=selected_count)
        )

    class Meta:
        model = Product
        exclude = ["featured_image"]
