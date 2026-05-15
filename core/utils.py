from django.utils.html import format_html


def get_admin_link(url: str, label: str) -> str:
    """
    Returns a safe HTML anchor tag for the Django admin.
    """
    return format_html('<a href="{}">{}</a>', url, label)
