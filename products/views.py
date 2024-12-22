from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.db.models import Q
from django.db import IntegrityError


from .forms import ProductForm, ImageForm, VariationForm
from .models import Image, Product, Variation
from .forms import ProductForm, ImageForm, VariationForm
from .models import Image, Product, Variation

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

    print(search)

    if search:
        products = Product.objects.filter(
            product_name__icontains = search,
            description__icontains = search,
            is_deleted = False,
        )
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
        variations = Variation.objects.filter(product=product, is_active=True)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('listproduct')
    except Variation.DoesNotExist:
        messages.error(request, 'Vatiation not found')

    storage = None
    color = None
    storage_price = None
    color_price = None
    if variations:
        print('variations und')
        for variation in variations:
            if variation.variation_category == 'storage size':
                storage = 'storage'
                if variation.price:
                    storage_price = 'storage price'
            elif variation.variation_category == 'color':
                color = 'color'
                if variation.price:
                    color_price = 'color price'

    print('Ellam', storage, color, color_price, storage_price)
    
    context = {
        'product':product,
        'variations' : variations,
        'storage' : storage,
        'color' :color,
        'storage_price' : storage_price,
        'color_price' : color_price,
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

        for image in existing_images:
            # Check if a new image is uploaded for this existing image
            new_image = request.FILES.get(f'image_{image.id}')
            clear_image = request.POST.get(f'clear_image_{image.id}')
            if new_image:
                # Update the existing image with the new one
                image.image = new_image
                image.save()
            
            if clear_image:
                image.delete()

        if form.is_valid():
            form.save()
        
        if imgform:
            if imgform.is_valid():

                # Save new images
                images = imgform.cleaned_data.get('image')
                if images:
                    # Delete existing images before saving new ones (optional, depending on your preference)
                    Image.objects.filter(product=item).delete()
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
        product.product_name = product.product_name + "_DELETED"
        product.slug = product.slug + "_DELETED"
        product.is_deleted = True
        product.save()
        messages.success(request, 'Product successfully deleted.')
        return redirect('listproduct')
    except Product.DoesNotExist:
        messages.error(request, 'Product not found.')
    return redirect('listproduct')


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def add_variation(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized')
        return redirect('userhome')
    
    products = Product.objects.filter(is_available=True, is_deleted=False)
    
    if request.POST:
        variation_form = VariationForm(request.POST)

        if variation_form.is_valid():
            variation_form.save()
            messages.success(request, 'Variation added')
            return redirect('add_variations')
        
    else:
        variation_form = VariationForm()

    context = {
        'variation_form' : variation_form,
        'products' : products,
    }
    
    return render(request, 'add_variations.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def list_variation(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized')
        return redirect('userhome')
    
    search = request.GET.get('search')

    if search:
        variations = Variation.objects.filter(
            Q(variation_category__icontains=search) |
            Q(variation_value__icontains=search) |
            Q(product__product_name__icontains=search)
        )
    else:
        variations = Variation.objects.all()

    context = {
        'variations' : variations,
    }

    return render(request, 'list_variations.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def edit_variations(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized')
        return redirect('userhome')

    variation = Variation.objects.get(pk=pk)
    if request.POST:
        variation_form = VariationForm(request.POST, instance=variation)

        if variation_form.is_valid():
            variation_form.save()
            messages.success(request, 'Variation edited successfully')
            return redirect('list_variations')
        
    else:
        variation_form = VariationForm(instance=variation)

    context = {
        'variation_form' : variation_form,
    }
    
    return render(request, 'add_variations.html', context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def delete_variations(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You are not authorized')
        return redirect('userhome')

    try:
        variation = Variation.objects.get(pk=pk)
        variation.delete()
        messages.success(request, 'Variation deleted successfully')
        return redirect('list_variations')
    except Variation.DoesNotExist:
        messages.warning(request, 'Requested vaiation does not exist')
        return redirect('list_variations')

