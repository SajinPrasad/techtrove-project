from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from .forms import ProductOfferForm, CategoryOfferForm
from .models import ProductOffer, CategoryOffer

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def create_offer(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized to this page')
        return redirect('adminlogin')

    if request.method == 'POST':
        offer_type = request.POST.get('offer_type', '')

        if offer_type == 'product':
            form_class = ProductOfferForm(request.POST)
        elif offer_type == 'category':
            form_class = CategoryOfferForm(request.POST)
        else:
            messages.error(request, 'Invalid offer type selection')
            return redirect('create_offer')

        if form_class.is_valid():
            try:
                form_class.save()
                messages.success(request, 'Offer created successfully')
                return redirect('list_offers')
            except IntegrityError:
                messages.error(request, 'An error occurred while saving the offer. Please check for duplicate entries or invalid data.')
                return redirect('create_offer')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {e}')
                return redirect('create_offer')

    else:
        form_class = None

    context = {
        'form_class': form_class,
    }

    return render(request, 'create_offer.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def list_offers(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized to view this page')
        return redirect('adminlogin')

    product_offers = ProductOffer.objects.all()
    category_offers = CategoryOffer.objects.all()

    context = {
        'product_offers' : product_offers,
        'category_offers' : category_offers,
    }

    return render(request, 'list_offers.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def offer_edit(request, pk, type):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized to view this page')
        return redirect('adminlogin')

         
    if request.POST:
        offer_type = request.POST.get('offer_type', '')

        if offer_type == 'product':
            try:
                offer = ProductOffer.objects.get(pk=pk)
            except ProductOffer.DoesNotExist:
                messages.error(request, "Offer doesn't exitst")
            form_class = ProductOfferForm(request.POST, instance=offer)
        elif offer_type == 'category':
            try:
                offer = CategoryOffer.objects.get(pk=pk)
            except CategoryOffer.DoesNotExist:
                messages.error(request, "Offer doesn't exitst")
            form_class = CategoryOfferForm(request.POST, instance=offer)
        else:
            messages.error(request, 'Invalid offer type selection')
            return redirect('create_offer')
        
        if form_class.is_valid():
            try:
                form_class.save()
                messages.success(request, 'Offer created successfully')
                return redirect('list_offers')
            except IntegrityError:
                messages.error(request, 'An error occurred while saving the offer. Please check for invalid data.')
                return redirect('create_offer')
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {e}')
                return redirect('create_offer')
    else:
        try:
            form_class = ProductOfferForm(instance=offer)
        except Exception:
            form_class = CategoryOfferForm(instance=offer)

    context = {
        'form_class' : form_class,
    }

    return render(request, 'create_offer.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def delete_offer(request, pk, type):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorised to this page')
        return redirect('adminlogin')
    
    if type == 'product':
        try:
            offer = ProductOffer.objects.get(pk=pk)
        except ProductOffer.DoesNotExist:
            messages.error(request, "Offer doesn't exitst")
    elif type == 'category':
        try:
            offer = CategoryOffer.objects.get(pk=pk)
        except CategoryOffer.DoesNotExist:
            messages.error(request, "Offer doesn't exitst")
    
    try:
        offer.delete()
        messages.success(request, 'Offer delted successfully')
        category_offers = CategoryOffer.objects.all()
        product_offers = ProductOffer.objects.all()
        context = {
            'product_offers' : product_offers,
            'category_offers' : category_offers,
        }
        return render(request, 'list_offers.html', context)
    except Exception as e:
        messages.error(request, f'Error: {e}')
        return redirect('list_offers')

    
    

