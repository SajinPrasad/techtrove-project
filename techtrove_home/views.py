from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from product_category.models import Category
from products.models import Product

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
@login_required(login_url='register')
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
