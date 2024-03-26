from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages

from user_accounts.models import Account
from orders.models import Order
from products.models import Product

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('adminhome')
    
    user = None
    err_msg = None
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('adminhome')
        else:
            try:
                existing_user = Account.objects.get(email=email)
                if existing_user.is_superuser:
                    err_msg = "Invalid Password"
                else:
                    err_msg = 'You are not authorised to this page'
            except Account.DoesNotExist:
                err_msg = "User doesn't exist"

    context = {
        'err_msg' : err_msg,
    }
    return render(request, 'admin_login.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def adminhome(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access the admin panel.')
        return redirect('adminlogin')
    
    orders = Order.objects.all().order_by('-created_at')[:5]
    order_count = Order.objects.filter(status='Delivered').count()
    user_registered = Account.objects.filter(is_verified=True, is_blocked=False).count()
    products_available = Product.objects.filter(is_available=True, stock__gte=1, is_deleted=False).count()

    context = {
        'order_count' : order_count,
        'user_registered' : user_registered,
        'products_available' : products_available,
        'orders' : orders,
    }

    return render(request, 'admin_home.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def admin_logout(request):
    if request.POST:
        logout(request)
        return redirect('adminlogin')
    return redirect('adminhome')



