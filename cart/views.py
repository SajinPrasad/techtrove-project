from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
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
from wishlist.models import Wishlist

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def cart_view(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to add items to cart')

    cart = None
    cart_items = []
    total = 0
    quantity = 0
    product_totals = []
    coupon_applied = None
    valid_coupons = []

    current_user = request.user.id
    try:
        cart = Cart.objects.get(user=current_user)
    except Cart.DoesNotExist:
        messages.info(request, 'No items in the cart yet')
        return render(request, 'cart.html')
    coupon_applied = cart.coupon_code
    try:
        coupon_instance = Coupon.objects.get(code=coupon_applied)
        if cart.cart_total < coupon_instance.minimum_order_value:
            cart.coupon_code = None
            cart.save()
    except Coupon.DoesNotExist:
        coupon_instance = None
    
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

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def add_to_cart(request, product_id):
    referring_url = request.META.get('HTTP_REFERER', '/')
    request.session['referring_url'] = referring_url

    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if not (1 <= quantity <= 5):
            messages.warning(request, 'Please enter a quantity between 1 and 5.')
            return redirect(reverse('singleproduct', kwargs={'category_slug': product.category.slug, 'product_slug': product.slug}))

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            messages.info(request, 'Please login to add items to cart')
            return redirect('register')

        cart_item = None

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
        except CartItem.DoesNotExist:
            cart_item = None

        if cart_item is not None:
            wishlist = request.POST.get('wishlist')
            if product.stock == cart_item.quantity:
                messages.warning(request, f'You already added maximum available quantity for this product')
                return redirect(referring_url)

            if quantity <= product.stock and cart_item.quantity < 5:
                cart_item.quantity += quantity
                if cart.cart_total:
                    cart.cart_total += cart_item.product.price * quantity
                else:
                    cart.cart_total = cart_item.product.price * quantity
                cart.save()
                messages.success(request, f'{quantity} item(s) added to your cart.')
                cart_item.save()

                if wishlist:
                    wishlist_item = Wishlist.objects.get(product=cart_item.product)
                    wishlist_item.delete()
                    
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
            wishlist = request.POST.get('wishlist')
            if quantity <= product.stock:
                cart_item = CartItem.objects.create(
                    product=product,
                    quantity=quantity,
                    cart=cart
                )

                cart.cart_total = cart_item.product.price * quantity
                cart.save()

                messages.success(request, f'{quantity} item(s) added to your cart.')
                cart_item.save()

                if wishlist:
                    wishlist_item = Wishlist.objects.get(product=cart_item.product)
                    wishlist_item.delete()

                return redirect('cart')
            else:
                messages.warning(request, f'Exceeds the available stock for this product. You can only pick {product.stock}')
                return redirect(referring_url)

    else:
        max_quantity = min(product.stock, 5)
    
    # Calculate max_quantity after the CartItem creation
    max_quantity = min(cart_item.product.stock, 5) if cart_item and cart_item.product else 0

    context = {
        'product': product,
        'max_quantity': max_quantity,
    }

    return render(request, 'cart.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def update_cart_item(request, cart_item_id):
    cart = Cart.objects.get(user=request.user)
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
        elif new_quantity == 0:
            messages.warning(request, "Quantity can't be zero...")
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
            if new_quantity <= cart_item.product.stock:
                cart_item.quantity = new_quantity
                diff = abs(old_quantity - new_quantity)
                if new_quantity < old_quantity:
                    cart.cart_total -= cart_item.product.price * diff
                    cart.save()
                elif new_quantity > old_quantity:
                    cart.cart_total += cart_item.product.price * diff
                    cart.save()
            else:
                messages.warning(request, f'Only {cart_item.product.stock} numbers are available for this product.')
                return redirect('cart')
                
            cart_item.save()
            
            messages.success(request, 'Cart updated.')

            return redirect('cart')
            

    return redirect('cart')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def delete_cart_item(request, cart_item_id):
    referring_url = request.META.get('HTTP_REFERER', '/')
    request.session['referring_url'] = referring_url
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(pk=cart_item_id, is_active=True)
        product = cart_item.product
        quantity_to_add_back = cart_item.quantity

        cart.cart_total -= product.price * quantity_to_add_back
        cart.save()

        cart_item.delete()

        messages.success(request, 'Item removed from cart')
        
    except CartItem.DoesNotExist:
        messages.error(request, 'Cart item not found')

    return redirect(referring_url)




