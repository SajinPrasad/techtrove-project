from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from .models import Wishlist
from products.models import Product

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='landingpage')
def wishlist_view(request):
    products = Wishlist.objects.filter(user=request.user)

    context = {
        'products' : products,
    }

    return render(request, 'wishlist.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='landingpage')
def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    
    existing_wishlist_entry = Wishlist.objects.filter(user=request.user, product=product).first()

    if existing_wishlist_entry:
        referring_url = request.META.get('HTTP_REFERER', '/')
        request.session['referring_url'] = referring_url
        messages.warning(request, 'Product already exists in whishlist')
        return redirect(referring_url)
    else:
        referring_url = request.META.get('HTTP_REFERER', '/')
        request.session['referring_url'] = referring_url
        wishlist = Wishlist.objects.create(
            user=request.user,
            product=product,
            quantity=1, 
        )
        messages.success(request, 'Product added to wishlist')

        return redirect(referring_url)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='landingpage')
def delete_item_wishlist(request, pk):
    referring_url = request.META.get('HTTP_REFERER', '/')
    request.session['referring_url'] = referring_url
    try:
        product = Wishlist.objects.get(pk=pk)
        product.delete()
        messages.success(request, 'Item removed from wishlist')
        return redirect(referring_url)
    except Wishlist.DoesNotExist:
        messages.error(request, 'Product does not exist in wishlist')
        return redirect(referring_url)
        


