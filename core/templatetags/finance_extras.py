from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    if mapping is None:
        return None
    return mapping.get(key)


@register.filter
def attr(obj, name):
    return getattr(obj, name, "")


@register.filter
def annual_sum(mapping):
    if not mapping:
        return Decimal("0.00")
    return sum(mapping.values(), start=Decimal("0.00"))


@register.filter
def brl(value):
    value = value or Decimal("0.00")
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
