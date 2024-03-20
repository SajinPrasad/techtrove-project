from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.urls import reverse
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
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.contrib.auth.hashers import make_password

from .models import Account
from .forms import RegistrationForm, UserEditForm

CACHE_TIMEOUT = 600

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
            username = email.split('@')[0] or slugify(email.split('@')[0])

            hashed_password = make_password(password)

            if Account.objects.filter(email=email).exists():
                messages.error('This email is already registered, try another one.')
            
            else:
                user = Account.objects.create_user(
                first_name=first_name, 
                last_name=last_name, 
                email=email, 
                password=hashed_password, 
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
            messages.success(request, 'You are successfully registered with us please verify OTP ')

            red = redirect(f'/user/verify/{user.id}/')

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
                profile = get_object_or_404(Account, id=uid)
                # Rest of your code...
            except Account.DoesNotExist:
                return HttpResponse('User not found')

            # Check if the 'can_otp_enter' cookie is set
            if request.COOKIES.get('can_otp_enter') is not None:
                stored_otp = request.session['otp']
                
                entered_otp = request.POST.get('otp')

                if int(stored_otp) == int(entered_otp):
                    profile.is_verified = True
                    profile.save()
                    messages.success(request, 'Your account has been verified successfully')

                    # Redirect to the login page after successful activation
                    red=redirect("register")
                    red.set_cookie('verified', True)
                    return red
                else:
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

        if user is not None and user.is_verified:
            if user.is_blocked:
                messages.error(request, 'Your account is blocked. Please contact the administrator.')
                return redirect('register')
            else:
                login(request, user)
                return redirect('userhome')
        else:
            try:
                Account.objects.get(email=email)
                messages.success(request, 'Invalid password!')
                return redirect('register')
            except Account.DoesNotExist:
                messages.success(request, 'User not found!')
                return redirect('register')
                
    return render(request, 'login_register.html')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='register')
def logout(request):
    if request.POST:
        auth.logout(request)
        return redirect('landingpage')
    return redirect('userhome')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def admin_userlist(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    users = Account.objects.all()
    context = {
        'users':users
    }
    return render(request, 'admin_userlist.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def admin_user_edit(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    
    user = get_object_or_404(Account, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User details updated successfully.')
            return redirect('adminuserlist')  
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'admin_user_edit.html', {'form': form, 'user': user})

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            
            otp = random.randint(100000, 999999)

            # Consider using a safer method to store OTP, like Django's cache framework

            # Store OTP in session (consider safer alternatives)
            request.session['otp_fp'] = otp
            request.session['otp_timestamp'] = str(timezone.now())

            # Send OTP via email
            try:
                send_mail('Reset techtrove password', f"Verify your mail by OTP: {otp}", settings.EMAIL_HOST_USER, [email], fail_silently=False)
            except Exception as e:
                messages.error(request, "Failed to send email. Please try again later.")
                return redirect('register')
            
            # Set a cookie for OTP entry
            red = redirect(f'/{user.id}/otp_fp/verify/')
            red.set_cookie("can_otp_enter", True, max_age=600)  # Adjust max_age as needed
            messages.success(request, 'For reset password pleas verify the OTP sent to your email.')
            return red
            
        else:
            messages.error(request, "The account doesn't exist!")
            return redirect('forgotpassword')
        
    return render(request, 'forgot_password.html')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def otp_fp_verify(request, uid):
    try:
        profile = Account.objects.get(id=uid)
        if request.method == "POST":
            stored_otp = request.session.get('otp_fp')
            entered_otp = request.POST.get('otp')

            if stored_otp and entered_otp and int(stored_otp) == int(entered_otp):
                # Clear OTP session variables after successful verification
                del request.session['otp_fp']
                del request.session['otp_timestamp']
                
                request.session['uid'] = profile.id
                messages.success(request, 'Now you can edit your password.')
                
                # Redirect to the reset_password page after successful activation
                return redirect('resetpassword', user_id=profile.id)

            messages.error(request, 'Wrong OTP. Try again')

    except ObjectDoesNotExist:
        messages.error(request, 'Error: Account not found.')
    except MultipleObjectsReturned:
        messages.error(request, 'Error: Multiple accounts found for the given UID.')

    return render(request, "otp_fp.html", {'id': uid})


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def reset_password(request, user_id):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            try:
                user = Account.objects.get(pk=user_id)
                user.set_password(password)
                user.save()
                # Update the session auth hash to prevent logout after password change
                update_session_auth_hash(request, user)
                messages.success(request, 'Password reset successful')
                return redirect('register')
            except ObjectDoesNotExist:
                messages.error(request, 'User does not exist.')
                return redirect('resetpassword', user_id=user_id)
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('resetpassword', user_id=user_id)
    else:
        return render(request, "reset_password.html", {'user_id': user_id})
    

