from typing import Dict, Any
from .models import CartItem


def cart_info(request) -> Dict[str, Any]:
    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user).select_related('medicine')
        cart_map = {str(ci.medicine_id): ci.quantity for ci in items}
        count = sum(ci.quantity for ci in items)
    else:
        cart_map = {}
        count = 0
    return {
        'cart_count': count,
        # Expose mapping for template badges and JS prefill
        'session_cart': cart_map,
    }


