from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(str(key)) or mapping.get(int(key))
    except Exception:
        return None


