from django.shortcuts import render, redirect
from uuid import UUID
import random
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth import login, logout as user_logout, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.utils.text import slugify
from django.contrib import messages, auth
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404

from .models import Accounts
from .forms import RegistrationForm

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def register(request):
    if request.user.is_authenticated:
        return redirect('userhome')

    if request.method == 'POST':
        frm = RegistrationForm(request.POST)
        if frm.is_valid():
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['otp_timestamp'] = str(timezone.now())

            first_name = frm.cleaned_data['first_name']
            last_name = frm.cleaned_data['last_name']
            phone_number = frm.cleaned_data['phone_number']
            email = frm.cleaned_data['email']
            password = frm.cleaned_data['password']
            #username = email.split("@")[0]
            username = email.split('@')[0] or slugify(email.split('@')[0])

            user = Accounts.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                email=email, 
                password=password, 
                username=username,
                )
            
            user.phone_number = phone_number
            user.is_verified = False
            user.email_token = otp
            user.save()

            frm = RegistrationForm()

            messages.success(request, 'Account created successfully.')

            subject = "Activate your account"
            message = f"Activate your account using this otp: {otp}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

            red = redirect(f'/verify/{user.id}/')

            red.set_cookie("can_otp_enter",True,max_age=600)
            messages.success(request, 'You are successfully registered with us please verify OTP ')
            return red

    else:
        frm = RegistrationForm()

    context = {'frm': frm}
    return render(request, 'login_register.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def verify(request, uid):
    if request.user.is_authenticated:
        return redirect('userhome')
    
    if request.method == "POST":
        try:
            try:
                profile = get_object_or_404(Accounts, id=uid)
                # Rest of your code...
            except Accounts.DoesNotExist:
                return HttpResponse('User not found')

            # Check if the 'can_otp_enter' cookie is set
            if request.COOKIES.get('can_otp_enter') is not None:
                stored_otp = request.session['otp']
                
                entered_otp = request.POST.get('otp')

                if int(stored_otp) == int(entered_otp):
                    profile.is_verified = True
                    profile.save()

                    # Redirect to the login page after successful activation
                    red=redirect("register")
                    red.set_cookie('verified', True)
                    return red

                messages.success(request, 'Wrong OTP. Try again')

            return redirect(request.path)  # Redirect to the same page on OTP failure

        except MultipleObjectsReturned:
            # Handle the case where more than one object is returned
            messages.success(request, 'Error: Multiple accounts found for the given UID.')
            return redirect('register')  # Redirect to an error page or handle it appropriately

    return render(request, "otp.html", {'id': uid})

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def login_page(request):
    if request.user.is_authenticated:
        return redirect('userhome')
    
    if request.method == 'POST':
        email =  request.POST['email']
        password = request.POST['password']

        user = authenticate(email=email, password=password)
        print(user)

        if user is not None and user.is_verified:
            login(request, user)
            return redirect('userhome')
        else:
            try:
                Accounts.objects.get(email=email)
                messages.success(request, 'Invalid password!')
            except Accounts.DoesNotExist:
                messages.success(request, 'User not found!')
                
    return render(request, 'login_register.html')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def logout(request):
    if request.POST:
        auth.logout(request)
        return redirect('register')
    return redirect('userhome')

