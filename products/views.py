from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control


from .forms import ProductForm, ImageForm
from .models import Image, Product

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def add_product(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    imgform = None
    if request.POST:
        form = ProductForm(request.POST)
        images = request.FILES.getlist('image')
        if form.is_valid():
            f = form.save(commit=False)
            form.save()
            form = ProductForm()
            for i in images:
                Image.objects.create(product=f, image=i)
            messages.success(request, 'Added new prodect')
            return redirect('addproduct')
    else:
        form = ProductForm()
        imgform = ImageForm()
    context = {'form':form, 'imgform':imgform}
    return render(request, 'add_product.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def list_product(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    products = Product.objects.filter(is_deleted=False)
    context = {
        'products':products
    }
    return render(request, 'product_list.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def single_product_admin(request, category_slug, product_slug):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    try:
        single = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single':single,
    }
    return render(request, 'techtrove_home/single_product.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def edit_product(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    item = Product.objects.get(pk=pk)
    if request.POST:
        form = ProductForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('listproduct')
    else:
        form = ProductForm(instance=item)

    return render(request, 'add_product.html', {'form':form})

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
def soft_delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        product.is_deleted = True
        product.save()
        messages.success(request, 'Product successfully deleted.')
        return redirect('listproduct')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
    return redirect('listproduct')
