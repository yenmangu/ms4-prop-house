from commerce.models import Order
from django import forms
from django.db.models import Q, QuerySet
import django_filters as df
from warehouse.models import HireRecord


class UserOrderFilter(df.FilterSet):

    # Search by Order Number or Asset Name
    q = df.CharFilter(
        method="filter_search",
        label="SEARCH_ASSETS",
        widget=forms.TextInput(
            attrs={
                "placeholder": "ID_OR_ASSET_NAME",
                "class": "mono-font",
            }
        ),
    )

    STATUS_CHOICES = (
        ("active", "ACTIVE_HIRES"),
        ("returned", "RETURNED_HIRES"),
    )

    state = df.ChoiceFilter(
        choices=STATUS_CHOICES,
        method="filter_by_state",
        label="HIRE_STATE",
        empty_label="ALL_RECORDS",
    )

    class Meta:
        model = HireRecord
        fields = []

    def filter_search(self, queryset: QuerySet, name, value):

        return queryset.filter(
            Q(order_item__order__id__icontains=value)
            | Q(stock_item__product__name__icontains=value),
        ).distinct()

    def filter_by_state(self, queryset: QuerySet, name, value):
        if value == "active":
            return queryset.filter(returned_date__isnull=True)

        if value == "returned":
            return queryset.filter(returned_date__isnull=False)

        return queryset
