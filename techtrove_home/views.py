from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from product_category.models import Category
from products.models import Product
from datetime import date
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import Q
from orders.models import OrderProduct

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def landing_page(request):
    products = Product.objects.filter(is_deleted=False, is_available=True)
    items = Category.objects.all()
    context = {
        'products':products, 
        'items':items,
        }
    return render(request, 'landing.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='landingpage')
def user_home(request):
    products = Product.objects.filter(is_deleted=False, is_available=True)
    items = Category.objects.all()
    context = {
        'products':products, 
        'items':items,
        }
    return render(request, 'user_home.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def single_product(request, category_slug, product_slug):
    items = Category.objects.all()
    try:
        single = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single':single,
        'items':items,
    }
    return render(request, 'single_product.html', context)

# Views for shop
@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def shop_view(request):
    products = Product.objects.filter(is_deleted=False, is_available=True)
    items = Category.objects.all()
    has_products = products.exists()
    context = {
        'products': products, 
        'items': items,
        'has_products': has_products,
    }
    return render(request, 'shop.html', context)

# Views for filtering the categories
@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def category_filter_shop(request, cat_id):
    products = Product.objects.filter(category=cat_id, is_deleted=False, is_available=True)
    items = Category.objects.all()
    has_products = products.exists()
    context = {
        'products': products, 
        'items': items,
        'has_products': has_products,
    }
    return render(request, 'shop.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def product_filter(request):
    selected_category = request.GET.get('category', None)
    order_by = request.GET.get('order_by', None)
    search_query = request.GET.get('search', None)

    products = Product.objects.filter(is_deleted=False, is_available=True)

    if selected_category:
        products = products.filter(category=selected_category)
        available_products = products
    else:
        products = Product.objects.filter(is_deleted=False, is_available=True)
        available_products = products

    # if 'search' in request.GET:
    #     products = available_products.filter(Q(product_name__icontains=search_query) | Q(description__icontains=search_query))
            
    if order_by:
        if order_by == 'low_to_high':
            products = available_products.order_by('price')
            available_products = products
        elif order_by == 'high_to_low':
            products = available_products.order_by('-price')
            available_products = products
        elif order_by == 'a_to_z':
            products = available_products.order_by('product_name')
            available_products = products
        elif order_by == 'z_to_a':
            products = available_products.order_by('-product_name')
            available_products = products
        elif order_by == 'new_arrivals':
            today = date.today()
            products = available_products.order_by('-created_date')
            available_products = products
            if not products.exists():
                messages.info(request, 'No products available')
        elif order_by == 'popularity':
            # Get all products and annotate them with total quantity ordered
            all_products = Product.objects.all().annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))
            
            # Sort products by popularity (total quantity ordered)
            popular_products = sorted(all_products, key=lambda x: x.total_quantity, reverse=True)

            # Separate available and unavailable products
            available_products = [product for product in popular_products if product.is_available and not product.is_deleted]

            # Display available products first, sorted by popularity
            products = available_products
            available_products = products

    if 'search' in request.GET:
        products = available_products.filter(Q(product_name__icontains=search_query) | Q(description__icontains=search_query))

    has_products = products

    context = {
        'products': products,
        'selected_category': selected_category, 
        'selected_order': order_by,
        'has_products' : has_products,      
    }

    return render(request, 'shop.html', context)

def search_products(request):
    search_query = request.GET.get('search')

    if 'search' in request.GET:
        if search_query:
            available_products = Product.objects.filter(is_deleted=False, is_available=True)
            products = available_products.filter(
                Q(product_name__icontains=search_query) | Q(description__icontains=search_query)
            )

    context = {
        'products' : products
    }

    return render(request, 'shop.html', context)


