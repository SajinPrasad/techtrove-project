from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from .utils import calculate_grand_total 
from itertools import zip_longest
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
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
        'cart_items' : cart_items,
    }

    return render(request, 'cart.html', context)

def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if not (1 <= quantity <= 5):
            messages.warning(request, 'Please enter a quantity between 1 and 5.')
            return redirect(reverse('singleproduct', kwargs={'category_slug': product.category.slug, 'product_slug': product.slug}))

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
                cart.save()

        cart_item = None

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
        except CartItem.DoesNotExist:
            cart_item = None

        if cart_item is not None:
            if quantity <= product.stock:
                cart_item.quantity += quantity
                cart_item.save()

                product.stock -= quantity
                product.save()

                messages.success(request, f'{quantity} item(s) added to your cart.')
                return redirect('cart')
            else:
                messages.warning(request, f'Exceeds the available stock for this product. Stock: {product.stock}')

        else:
            # Cart item does not exist
            if quantity <= product.stock:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=quantity,
                    cart=cart
                )
                cart_item.save()

                product.stock -= quantity
                product.save()

                messages.success(request, f'{quantity} item(s) added to your cart.')
                return redirect('cart')
            else:
                messages.warning(request, f'Exceeds the available stock for this product. You can only pick {product.stock}')
                return redirect(reverse('singleproduct', kwargs={'category_slug': product.category.slug, 'product_slug': product.slug}))

    else:
        max_quantity = min(product.stock, 5)
    
    # Calculate max_quantity after the CartItem creation
    max_quantity = min(cart_item.product.stock, 5) if cart_item and cart_item.product else 0

    context = {
        'product': product,
        'max_quantity': max_quantity,
    }

    return render(request, 'cart.html', context)


def update_cart_item(request, cart_item_id):
    if request.method == 'POST':
        quantity_str = request.POST.get('quantity')
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        product = cart_item.product

        try:
            new_quantity = int(quantity_str)
        except ValueError:
            return HttpResponseBadRequest("Invalid quantity")

        old_quantity = cart_item.quantity
        quantity_difference = new_quantity - old_quantity

        if new_quantity > 5:
            messages.info(request, 'You can only add up to 5 units per product.')
        elif new_quantity > (product.stock + old_quantity):
            if product.stock > 0:
                messages.warning(request, f'Only {product.stock} stock available, try within the limit.')
            elif product.stock == 0:
                messages.info(request, 'No stock available for this product')
        else:
            # Update cart item quantity
            cart_item.quantity = new_quantity
            cart_item.save()

            # Update product stock based on the quantity difference
            product.stock -= quantity_difference
            if product.stock < 0:
                product.stock = 0
            product.save()

            messages.info(request, 'Cart updated.')

    return redirect('cart')

def delete_cart_item(request, cart_item_id):
    try:
        cart_item = CartItem.objects.get(pk=cart_item_id, is_active=True)
        product = cart_item.product
        quantity_to_add_back = cart_item.quantity 

        cart_item.delete()  

        product.stock += quantity_to_add_back
        product.save()

        messages.info(request, 'Item removed from cart')
    except CartItem.DoesNotExist:
        messages.warning(request, 'Cart item not found')

    return redirect('cart')




