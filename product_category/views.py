from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages

from .forms import CategoryForm
from .models import Category

# Create your views here.

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def add_category(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    if request.POST:
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categorylist')
    else:
        form = CategoryForm()
    context = {'form':form}
    return render(request, 'add_category.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def edit_category(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    item = Category.objects.get(pk=pk)
    if request.POST:
        form = CategoryForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('categorylist')
    else:
        form = CategoryForm(instance=item)

    return render(request, 'add_category.html', {'form':form})

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def category_soft_delete(request, pk):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    try:
        category = Category.objects.get(pk=pk)
        category.is_deleted = True
        category.save()
        messages.success(request, 'Category successfully deleted.')
        return redirect('categorylist')
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
    return redirect('categorylist')

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def category_list(request):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    
    search = request.GET.get('search')

    if search:
        categories = Category.objects.filter(
            is_deleted = False,
            category_name__icontains = search,
            description__icontains = search,
        )
    else:
        categories = Category.objects.filter(is_deleted=False)
        
    context = {
        'categories':categories
    }
    return render(request, 'cat_list.html', context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True, max_age=0)
@login_required(login_url='adminlogin')
def single_category(request, category_slug):
    if not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access this page.')
        return redirect('adminlogin')
    try:
        single = Category.objects.get(slug=category_slug)
    except Exception as e:
        raise e
    context = {
        'single':single,
    }
    
    return render(request, 'single_cat.html', context)

