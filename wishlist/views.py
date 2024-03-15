from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseBadRequest

from .models import Wishlist
from products.models import Product

# Create your views here.

def wishlist_view(request):
    products = Wishlist.objects.all()

    context = {
        'products' : products,
    }

    return render(request, 'wishlist.html', context)


def add_to_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)

    existing_wishlist_entry = Wishlist.objects.filter(user=request.user, product=product).first()

    if existing_wishlist_entry:
        existing_wishlist_entry.quantity += 1
        existing_wishlist_entry.save()
    else:
        wishlist = Wishlist.objects.create(
            user=request.user,
            product=product,
            quantity=1, 
        )

    return redirect('landingpage')

def delete_item_wishlist(request, pk):
    try:
        product = Wishlist.objects.get(pk=pk)
        product.delete()
        return redirect('wishlist')
    except Wishlist.DoesNotExist:
        messages.error(request, 'Product does not exist in wishlist')
        return redirect('wishlist')
        


