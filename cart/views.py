from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from itertools import zip_longest
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from products.models import Product
from .models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def calculate_grand_total(cart_items):
    grand_total = 0

    for cart_item in cart_items:
        total_price = cart_item.product.price * cart_item.quantity
        grand_total += total_price

    return grand_total

def cart_view(request):
    cart_items = []
    total = 0
    quantity = 0
    product_totals = []

    # Retrieve cart based on user status
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user, is_active=True)
    else:
        # For non-logged-in users, use session for cart identification
        cart_id = request.session.session_key
        if cart_id:
            try:
                cart = Cart.objects.get(cart_id=cart_id)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            except Cart.DoesNotExist:
                pass  # Ignore case where cart doesn't exist for non-logged-in users

    # Calculate totals and product-specific totals
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
        product_totals.append(cart_item.product.price * cart_item.quantity)

    zipped_data = zip_longest(cart_items, product_totals, fillvalue=None)

    context = {
        'total': total,
        'quantity': quantity,
        'zipped_data': zipped_data,
    }

    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  # Get the quantity, default to 1

        # Retrieve cart based on user status
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
                cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=quantity,
                cart=cart
            )
            cart_item.save()

        return redirect('cart')

    return render(request, 'cart.html', {'product': product})

@csrf_exempt
def update_cart_item(request, cart_item_id):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        quantity = request.POST.get('quantity', 1)  # Assuming you're sending the quantity via POST

        # Assuming you have a CartItem model with a ForeignKey to Product
        cart_item = get_object_or_404(CartItem, id=cart_item_id)

        # Update the quantity
        cart_item.quantity = quantity
        cart_item.save()

        # Calculate the new total price for the item
        total_price = cart_item.product.price * cart_item.quantity

        # Return updated data as JSON
        data = {
            'quantity': cart_item.quantity,
            'total_price': total_price,
            'grand_total': calculate_grand_total(),  # You need to implement this function
        }

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'})

def delete_cart_item(request, cart_item_id):
    if request.user.is_authenticated:
        # For logged-in users, filter by cart and user
        try:
            cart_item = CartItem.objects.get(pk=cart_item_id, cart__user=request.user, is_active=True)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass  # Handle case where item doesn't exist or user doesn't have permission

    else:
        # For non-logged-in users, filter by session cart_id
        try:
            cart_id = request.session.session_key
            if cart_id:
                cart_item = CartItem.objects.get(pk=cart_item_id, cart__cart_id=cart_id, is_active=True)
                cart_item.delete()
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            pass  # Handle cases where cart or item doesn't exist

    messages.info(request, 'Item removed from cart')
    return redirect('cart')




