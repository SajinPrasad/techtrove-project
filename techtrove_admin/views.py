from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from user_accounts.models import Accounts
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

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
        user = authenticate(email=email, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('adminhome')
        else:
            try:
                existing_user = Accounts.objects.get(email=email)
                if existing_user.is_superuser:
                    err_msg = "Invalid Password"
                else:
                    err_msg = 'You are not authorised to this page'
            except Accounts.DoesNotExist:
                err_msg = "User doesn't exist"
    return render(request, 'admin_login.html', {'err_msg':err_msg})

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def adminhome(request):
    return render(request, 'admin_home.html')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def admin_logout(request):
    if request.POST:
        logout(request)
        return redirect('adminlogin')
    return redirect('adminhome')


