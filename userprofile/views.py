from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import render
from django.contrib import messages

from user_accounts.models import Account
from . models import Address
from .forms import AddressForm
from .models import UserProfile

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='login')
def user_profile(request):
    up = UserProfile.objects.get(user=request.user)
    user = Account.objects.get(pk=request.user.pk)
    context = {
        'user':user,
        'up':up,
    }
    return render(request, 'user_profile.html', context)


@csrf_exempt
@login_required(login_url='login')
def update_user_data(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Parse incoming data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        # Parse birthdate string into datetime object
        birthdate_str = request.POST.get('birthdate')
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date() if birthdate_str else None
        gender = request.POST.get('gender')

        # Update user data in the database
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.phone_number = phone_number
        user.save()

        user_profile = UserProfile.objects.get(user=user)
        user_profile.birthdate = birthdate
        user_profile.gender = gender
        user_profile.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})
    
@login_required(login_url='register')
def add_address(request):
    if request.method == 'POST':
        a_frm = AddressForm(request.POST)
        if a_frm.is_valid():
            # Set the user before saving
            a_frm.instance.user = request.user
            a_frm.save()
            a_frm = AddressForm()
    else:
        a_frm = AddressForm()

    context = {
        'a_frm': a_frm
    }

    return render(request, 'add_address.html', context)

@login_required(login_url='register')
def list_address(request):
    addresses = Address.objects.filter(user=request.user)
    context = {
        'addresses':addresses
    }
    return render(request, 'list_address.html', context)

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
    
