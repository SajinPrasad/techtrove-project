from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from orders.models import Wallet
from . models import Address
from .forms import AddressForm, AccountForm, UserProfileForm
from .models import UserProfile
from orders.models import Order



def save_new_email(user, new_email):
    User = get_user_model()
    user_instance = User.objects.get(pk=user.pk)
    user_instance.email = new_email
    user_instance.save()

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def user_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    wallet, create = Wallet.objects.get_or_create(user=request.user)

    try:
        orders = Order.objects.filter(user=user_profile.user).order_by('-created_at')
    except Order.DoesNotExist:
        messages.info(request, 'You dont have any orders yet.')
    
    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        account_form = AccountForm(request.POST, instance=user_profile.user)

        if user_profile_form.is_valid() and account_form.is_valid():
            messages.success(request, 'Profile updated successfully.')
            user_profile_form.save()
            account_form.save()

            email = request.POST.get('email')

            if email:
                user = request.user
                otp = random.randint(100000, 999999)
                request.session['otp'] = otp
                request.session['otp_timestamp'] = str(timezone.now())
                request.session['email'] = email 

                subject = "Account verification - TechTrove"
                message = f"Verify your account using this otp: {otp}"
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                messages.success(request, 'You are successfully registered with us please verify OTP ')

                red = redirect(f'/user/verify/{user.id}/email/')

                red.set_cookie("can_otp_enter",True,max_age=600)
                messages.success(request, 'Please verify OTP ')
                return red
            
            return redirect('user_profile')

    else:
        user_profile_form = UserProfileForm(instance=user_profile)
        account_form = AccountForm(instance=user_profile.user)
    
    addresses = Address.objects.filter(user=request.user)

    context = {
        'user_profile_form': user_profile_form,
        'account_form': account_form,
        'orders': orders,
        'user_profile': user_profile,
        'wallet' : wallet,
        'addresses':addresses
    }

    return render(request, 'user_profile.html', context)

def verify_otp_email(request, uid):
    if request.method == "POST":
        # Check if the 'can_otp_enter' cookie is set
        if request.COOKIES.get('can_otp_enter') is not None:
            stored_otp = request.session['otp']
            
            entered_otp = request.POST.get('otp')

            if int(stored_otp) == int(entered_otp):
                new_email = request.session.get('email')
                try:
                    save_new_email(request.user, new_email)
                    messages.success(request, 'Your account has been verified successfully')

                    return redirect('user_profile')
                
                except IntegrityError:
                    messages.error(request, 'Email already exists. Please choose a different email.')

                return redirect('user_profile')
            
            else:
                messages.success(request, 'Wrong OTP. Try again')

        return redirect(request.path)  # Redirect to the same page on OTP failure

        
    return render(request, "otp_email.html", {'id': uid})


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if new_password == current_password:
            messages.error(request, "New password cannot be the same as the current password")
        elif new_password == confirm_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully')
                return redirect('user_profile')
            else:
                messages.error(request, 'Please enter a valid current password')
        else:
            messages.error(request, "Passwords do not match!")

    return redirect('user_profile')
    
    
@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def add_address(request):
    if request.method == 'POST':
        a_frm = AddressForm(request.POST)
        if a_frm.is_valid():
            # Set the user before saving
            a_frm.instance.user = request.user
            a_frm.save()
            a_frm = AddressForm()

            messages.success(request, 'New address added')
            return redirect('list_address')
    else:
        a_frm = AddressForm()

    context = {
        'a_frm': a_frm
    }

    return render(request, 'add_address.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def edit_address(request, pk):
    address = Address.objects.get(pk=pk)
    if request.method == 'POST':
        a_frm = AddressForm(request.POST, instance=address)
        if a_frm.is_valid():
            a_frm.save()
            a_frm = AddressForm()
            return redirect('list_address')
    else:
        a_frm = AddressForm(instance=address)
    
    context = {
        'a_frm':a_frm
    } 

    return render(request, 'add_address.html', context)

@login_required(login_url='register')
def delete_address(request, pk):
    addresses = Address.objects.get(pk=pk)
    addresses.delete()
    messages.success(request, 'Address deleted successfully.')
    addresses = Address.objects.all()

    context = {
        'addresses': addresses
        }
    return render(request, 'list_address.html', context)
    
