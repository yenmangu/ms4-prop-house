from django import template

register = template.Library()


@register.filter
def with_id(field, new_id):
    return field.as_widget(attrs={"id": new_id})
