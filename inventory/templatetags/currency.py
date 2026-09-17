from django import template

register = template.Library()


@register.filter
def money(value, symbol="৳"):
    try:
        return f"{symbol}{float(value):,.2f}"
    except Exception:
        return f"{symbol}0.00"


