from django.utils.html import format_html


def get_admin_link(
    url: str,
    label: str,
    hover_text=None,
) -> str:
    """
    Returns a safe HTML anchor tag for the Django admin.
    Supports optional full title hover-tooltip.
    """
    if not url:
        return label

    return format_html(
        '<a href="{url}" title="{title}">{label}</a>',
        url=url,
        title=hover_text or label,
        label=label,
    )
