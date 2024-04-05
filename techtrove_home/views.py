from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.utils import timezone
from product_category.models import Category
from products.models import Product, Variation
from datetime import date
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import Q
from offers.models import ProductOffer, CategoryOffer

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def landing_page(request):
    if request.user.is_authenticated:
        return redirect('userhome')
    
    all_products = Product.objects.annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))
            
    # Filter available and not deleted products
    available_products = all_products.filter(is_available=True, is_deleted=False)

    # Sort products by popularity (total quantity ordered)
    popular_products = available_products.order_by('-total_quantity')

    available_products = popular_products

    # Use available_products for further processing
    products = available_products

    items = Category.objects.all()
    context = {
        'products':products, 
        'items':items,
        }
    return render(request, 'landing.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='landingpage')
def user_home(request):
    all_products = Product.objects.annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))
            
    # Filter available and not deleted products
    available_products = all_products.filter(is_available=True, is_deleted=False)

    # Sort products by popularity (total quantity ordered)
    popular_products = available_products.order_by('-total_quantity')

    available_products = popular_products

    # Use available_products for further processing
    products = available_products

    items = Category.objects.all()
    context = {
        'products':products, 
        'items':items,
        }
    return render(request, 'user_home.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def single_product(request, category_slug, product_slug):
    try:
        single = Product.objects.get(category__slug=category_slug, slug=product_slug)
        variations = Variation.objects.filter(product=single, is_active=True)
    except Product.DoesNotExist:
        messages.warning(request, 'Product does not exist')
        return redirect('shop_view')
    except Variation.DoesNotExist:
        messages.warning(request, 'No variations found for this product')

    storage = None
    color   = None
    storage_price = None
    color_price = None
    if variations:
        for variation in variations:
            if variation.variation_category == 'storage size':
                storage = 'storage'
                if variation.price:
                    storage_price = 'storage price'
            elif variation.variation_category == 'color':
                color = 'color'
                if variation.price:
                    color_price = 'color price'
    
    # Check for product-specific offer
    product_offer = ProductOffer.objects.filter(
        product=single,
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now(),
    ).first()


    # Check for category-specific offer (if applicable)
    category_offer = CategoryOffer.objects.filter(
        category=single.category,
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now(),
    ).first()

    context = {
        'single' : single,
        'product_offer' : product_offer,
        'category_offer' : category_offer,
        'variations' : variations,
        'storage' : storage,
        'color' : color,
        'storage_price' : storage_price,
        'color_price' : color_price,
    }
    return render(request, 'single_product.html', context)

# Views for shop
@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def shop_view(request):
    products = Product.objects.filter(is_deleted=False, is_available=True)
    items = Category.objects.all()
    has_products = products.exists()

    # Get all products and annotate them with total quantity ordered
    all_products = Product.objects.annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))
    
    # Filter available and not deleted products
    available_products = all_products.filter(is_available=True, is_deleted=False)

    # Sort products by popularity (total quantity ordered)
    popular_products = available_products.order_by('-total_quantity')
            
    context = {
        'products': products, 
        'items': items,
        'has_products': has_products,
        'popular_products' : popular_products,
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

    all_products = Product.objects.annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))
            
    # Filter available and not deleted products
    available_products = all_products.filter(is_available=True, is_deleted=False)

    # Sort products by popularity (total quantity ordered)
    popular_products = available_products.order_by('-total_quantity')
    

    if selected_category:
        products = products.filter(category=selected_category)
        available_products = products
    else:
        products = Product.objects.filter(is_deleted=False, is_available=True)
        available_products = products
            
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
            all_products = Product.objects.annotate(total_quantity=Coalesce(Sum('orderproduct__quantity'), 0))
            
            # Filter available and not deleted products
            available_products = all_products.filter(is_available=True, is_deleted=False)

            # Sort products by popularity (total quantity ordered)
            popular_products = available_products.order_by('-total_quantity')

            # Assign popular_products back to available_products if needed
            available_products = popular_products

            # Use available_products for further processing
            products = available_products
            
    if 'search' in request.GET:
        products = available_products.filter(Q(product_name__icontains=search_query) | Q(description__icontains=search_query))

    has_products = products

    context = {
        'products': products,
        'selected_category': selected_category, 
        'selected_order': order_by,
        'has_products' : has_products,
        'popular_products' : popular_products,
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


