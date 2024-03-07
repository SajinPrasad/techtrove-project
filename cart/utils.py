from .models import CartItem

def calculate_grand_total(cart):
    cart_items = CartItem.objects.filter(cart=cart)
    grand_total = sum(item.total_price for item in cart_items)
    return grand_total