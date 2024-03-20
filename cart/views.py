from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.db import models
from django.utils import timezone
from itertools import zip_longest
from django.http import HttpResponseBadRequest
from django.db.models import Q 

from products.models import Product
from .models import Cart, CartItem
from coupons.models import Coupon
from offers.models import ProductOffer, CategoryOffer

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def cart_view(request):
    cart_items = []
    total = 0
    quantity = 0
    product_totals = []

    # Retrieve cart based on user status
    if request.user.is_authenticated:
        current_user = request.user
        try:
            cart = Cart.objects.get(user=current_user)
        except Cart.DoesNotExist:
            messages.info(request, 'No items in the cart yet')
            return render(request, 'cart.html')
        coupon_applied = cart.coupon_code
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        if not cart_items:
            cart.cart_total = 0
            cart.save()

        coupons = Coupon.objects.annotate(
            is_user_coupon=Q(user=current_user) | Q(applies_to_all_users=True)
        ).filter(
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
            is_user_coupon=True,
        )

        valid_coupons = []

        for coupon in coupons:
            user_usage_count = coupon.used_count_for_user(current_user)
            if user_usage_count < coupon.max_usage_count:
                valid_coupons.append(coupon)

    else:
        cart_id = request.session.session_key
        if cart_id:
            try:
                cart = Cart.objects.get(cart_id=cart_id)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                
            except Cart.DoesNotExist:
                pass 

    # Calculate totals and product-specific totals
    for cart_item in cart_items:
        discounted_price = 0

        # Check for product-specific offer
        product_offer = ProductOffer.objects.filter(
            product=cart_item.product,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
        ).first()


        # Check for category-specific offer (if applicable)
        category_offer = CategoryOffer.objects.filter(
            category=cart_item.product.category,
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
        ).first()

        # Apply offer with higher priority (product-specific or category-specific)
        if product_offer:
            discounted_price = product_offer.apply_offer(cart_item)
            product_offer_object = product_offer.get_the_offer(cart_item)

            if product_offer_object:
                cart_item.product_offer = product_offer_object
                cart_item.save()
        elif category_offer:
            discounted_price = category_offer.apply_offer(cart_item)
            category_offer_object = category_offer.get_the_offer(cart_item)
            
            if category_offer_object:
                cart_item.category_offer = category_offer_object
                cart_item.save()
        else :
            # If there is no discount we take actual price in discounted_price
            discounted_price = cart_item.product.price

        total += (discounted_price * cart_item.quantity)
        quantity += cart_item.quantity
        product_totals.append(discounted_price * cart_item.quantity)

        if not coupon_applied:
            cart.cart_total = total
            cart.save()

    print("Cart total", cart.cart_total)
    cart_total = cart.cart_total

    zipped_data = zip_longest(cart_items, product_totals, fillvalue=None)

    context = {
        'cart_total': cart_total,
        'quantity': quantity,
        'zipped_data': zipped_data,
        'cart_items' : cart_items,
        'valid_coupons' : valid_coupons,
        'coupon_applied' : coupon_applied,
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
            if quantity <= product.stock and cart_item.quantity < 5:
                cart_item.quantity += quantity
                messages.success(request, f'{quantity} item(s) added to your cart.')
                cart_item.save()

                product.stock -= quantity
                product.save()
                return redirect('cart')
            
            elif cart_item.quantity == 5:
                wishlist = request.POST.get('wishlist')
                messages.warning(request, f'Cart limit already exceeds for this item.')
                if not wishlist:
                    return redirect(reverse('singleproduct', kwargs={'category_slug': product.category.slug, 'product_slug': product.slug}))
                else:
                    return redirect('wishlist')
            else:
                messages.warning(request, f'Exceeds the available stock for this product. Stock: {product.stock}')
                return redirect(reverse('singleproduct', kwargs={'category_slug': product.category.slug, 'product_slug': product.slug}))

        else:
            # Cart item does not exist
            if quantity <= product.stock:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=quantity,
                    cart=cart
                )

                messages.success(request, f'{quantity} item(s) added to your cart.')
                cart_item.save()

                product.stock -= quantity
                product.save()

                return redirect('cart')
            else:
                messages.warning(request, f'Exceeds the available stock for this product. You can only pick {product.stock}')
                return redirect('cart')

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
            messages.warning(request, 'You can only add up to 5 units per product.')
            return redirect('cart')
        elif new_quantity > (product.stock + old_quantity):
            if product.stock > 0:
                messages.warning(request, f'Only {product.stock} stock available, try within the limit.')
                return redirect('cart')
            elif product.stock == 0:
                messages.info(request, 'No stock available for this product')
                return redirect('cart')
        else:
            # Update cart item quantity
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')

            # Update product stock based on the quantity difference
            product.stock -= quantity_difference
            if product.stock < 0:
                product.stock = 0
            
            product.save()
            return redirect('cart')
            

    return redirect('cart')

def delete_cart_item(request, cart_item_id):
    referring_url = request.META.get('HTTP_REFERER', '/')
    request.session['referring_url'] = referring_url
    try:
        cart_item = CartItem.objects.get(pk=cart_item_id, is_active=True)
        product = cart_item.product
        quantity_to_add_back = cart_item.quantity

        cart_item.delete()

        product.stock += quantity_to_add_back
        product.save()

        messages.success(request, 'Item removed from cart')
        
    except CartItem.DoesNotExist:
        messages.error(request, 'Cart item not found')

    return redirect(referring_url)



