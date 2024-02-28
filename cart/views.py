from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from itertools import zip_longest

from products.models import Product
from .models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def cart_view(request):
    total = 0
    quantity = 0
    product_totals = []  # Assuming you have a list of product totals

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            product_totals.append(cart_item.product.price * cart_item.quantity)

        zipped_data = zip_longest(cart_items, product_totals, fillvalue=None)

    except Cart.DoesNotExist:
        cart_items = []  # If cart doesn't exist, set cart_items to an empty list
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
        quantity = int(request.POST.get('quantity', 1))  # Get the quantity from the form, default to 1 if not provided

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
                cart=cart,
            )
            cart_item.save()

        return redirect('cart')

    return render(request, 'your_template.html', {'product': product})


