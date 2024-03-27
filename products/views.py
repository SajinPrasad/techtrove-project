from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django.db import transaction
from django.utils.decorators import method_decorator
from django.db import IntegrityError


from .forms import ProductForm, ImageForm, ImageFormSet
from .models import Image, Product

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def add_product(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')

    imgform = None

    if request.POST:
        form = ProductForm(request.POST)
        images = request.FILES.getlist('image')

        try:
            if form.is_valid():
                f = form.save(commit=False)

                # Set the category before saving
                category_id = request.POST.get('category')
                f.category_id = category_id

                form.save()
                form = ProductForm()

                for i in images:
                    Image.objects.create(product=f, image=i)

                messages.success(request, 'Added new product')
                return redirect('listproduct')
            
        except IntegrityError as e:
            messages.warning(request, 'Please select a valid category.')
            return redirect('addproduct')

    else:
        form = ProductForm()
        imgform = ImageForm()

    context = {'form': form, 'imgform': imgform}
    return render(request, 'add_product.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def list_product(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    
    search = request.GET.get('search')

    if search:
        try:
            products = Product.objects.filter(
                product_name__icontains = search,
                description__icontains = search,
                is_deleted = False,
            )
        except Product.DoesNotExist:
            messages.error(request, 'Products matching the query doesnot exists')
            return redirect('listproduct')
    else:
        products = Product.objects.filter(is_deleted=False)

    context = {
        'products':products
    }
    
    return render(request, 'product_list.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def single_product_admin(request, cat_slug, prod_slug):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    
    try:
        product = Product.objects.get(category__slug=cat_slug, slug=prod_slug)
    except Exception as e:
        messages.error(request, 'Product not found')
        return redirect('listproduct')
    
    context = {
        'product':product,
    }
    return render(request, 'single_product_admin.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def edit_product(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')

    try:
        item = Product.objects.get(pk=pk)
        existing_images = Image.objects.filter(product=item)
    except Product.DoesNotExist:
        messages.warning(request, 'Product not found.')
        return redirect('listproduct')
    except Image.DoesNotExist:
        messages.error(request, 'Image(s) not found')
        return redirect('listproduct')

    imgform = None
    if request.POST:
        form = ProductForm(request.POST, instance=item)
        imgform = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
        
        if imgform:
            if imgform.is_valid():
                # Delete existing images before saving new ones (optional, depending on your preference)
                Image.objects.filter(product=item).delete()

                # Save new images
                images = imgform.cleaned_data.get('image')
                if images:
                    for image in images:
                        Image.objects.create(product=item, image=image)

        messages.success(request, 'Product updated successfully.')
        return redirect('listproduct')
    else:
        form = ProductForm(instance=item)
        imgform = ImageForm()

    context = {
        'form': form, 
        'imgform': imgform,
        'existing_images' : existing_images
        }
    return render(request, 'edit_product.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def soft_delete_product(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    try:
        product = Product.objects.get(pk=pk)
        product.is_deleted = True
        product.save()
        messages.success(request, 'Product successfully deleted.')
        return redirect('listproduct')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
    return redirect('listproduct')



