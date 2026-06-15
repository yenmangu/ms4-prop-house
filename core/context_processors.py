from typing import TYPE_CHECKING

from django.http import HttpRequest
from django.urls import ResolverMatch

FILTER_DRAWER_VIEW_NAMES = {
    "catalogue:product_list",
    "catalogue:category_detail",
    "catalogue:search_results",
    "accounts:dashboard",
}


def drawer_context(request: HttpRequest) -> dict[str, bool]:
    resolver_match: ResolverMatch | None = getattr(
        request, "resolver_match", None
    )

    render_drawer = (
        resolver_match is not None
        and resolver_match.view_name in FILTER_DRAWER_VIEW_NAMES
    )

    return {
        "render_drawer": render_drawer,
    }
