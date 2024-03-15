from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from cart.models import CartItem, Cart
from coupons.models import Coupon
from .forms import CouponForm

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='userhome')
def apply_coupons(request):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    cart_total = cart.cart_total
    if request.POST:
        coupon_code = request.POST.get('code')
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code')
            return redirect('cart')

        if coupon.discount_type == 'fixed_amount' and cart_total >= coupon.minimum_order_value:
            discounted_amount = cart_total - coupon.discount_value
        elif coupon.discount_type == 'percentage' and cart_total >= coupon.minimum_order_value:
            discounted_amount = cart_total - coupon.discount_value * (cart_total / 100)
        else:
            messages.warning(request, f'This coupon is only applicable for orders worth rupees {coupon.minimum_order_value}')
            return redirect('cart')

        cart.cart_total = discounted_amount
        cart.coupon_name = coupon.name
        cart.coupon_code = coupon.code
        cart.save()
        
        print("Cart total 2 : ", cart.cart_total)

        coupon.used_count += 1
        coupon.save()

    messages.success(request, 'Coupon applied successfully')

    return redirect('cart')
    

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='userhome')
def remove_coupons(request, coupon_applied):
    current_user = request.user
    cart = Cart.objects.get(user=current_user)
    cart_total = cart.cart_total

    coupon = Coupon.objects.get(code=coupon_applied)

    if coupon.discount_type == 'fixed_amount':
        total = cart_total + coupon.discount_value

    elif coupon.discount_type == 'percentage':
        total = cart_total / (1 - coupon.discount_value / 100)

    elif cart_total <= coupon.minimum_order_value:
        messages.warning(request, f'This coupon is only applicable for orders worth rupees {coupon.minimum_order_value}')

    cart.cart_total = total
    cart.coupon_name = None
    cart.coupon_code = None
    cart.save()

    coupon.used_count -= 1
    coupon.save()

    messages.success(request, 'Coupon removed successfully')

    return redirect('cart')


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def add_coupons(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized to view this page')
        return redirect('adminlogin')
    
    if request.POST:
        form = CouponForm(request.POST)

        try:
            if form.is_valid:
                form.save()
                form = CouponForm()
                return redirect('list_coupons')
            
        except IntegrityError as e:
            messages.warning(request, 'Invalid entry found')
            return redirect('add_coupons')
        
    else:
        form = CouponForm()

    context = {
        'form' : form,
    
    }

    return render(request, 'add_coupons.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def list_coupons(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized to view this page')
        return redirect('adminlogin')

    coupons = []
    try:
        coupons = Coupon.objects.all()
    except Coupon.DoesNotExist:
        messages.info(request, 'No coupons found')

    context = {
        'coupons' : coupons,
    }

    return render(request, 'list_coupons.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def edit_coupons(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized to view this page')
        return redirect('adminlogin')

    coupon = Coupon.objects.get(pk=pk)
    
    if request.POST:
        form = CouponForm(request.POST, instance=coupon)
        
        if form.is_valid():
            try:
                form.save()
            except IntegrityError as e:
                messages.warning(request, 'Wrong entry found')

            form = CouponForm()
            return redirect('list_coupons')
    else:
        form = CouponForm(instance=coupon)

    context = {
        'form' : form,
    }

    return render(request, 'add_coupons.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def delete_coupons(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized to view this page')
        return redirect('adminlogin')

    try:
        coupon = Coupon.objects.get(pk=pk)
        coupon.delete()
        messages.success(request, 'Coupon deleted successfully')
    except Coupon.DoesNotExist:
        messages.warning(request, 'Coupon does not exist')

    coupons = Coupon.objects.all()

    context = {
        'coupons': coupons,
    }

    return render(request, 'list_coupons.html', context)


