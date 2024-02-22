from django.shortcuts import render, redirect
from .forms import CategoryForm
from .models import Category

# Create your views here.

def add_category(request):
    if request.POST:
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('addcategory')
    else:
        form = CategoryForm()
    context = {'form':form}
    return render(request, 'cart.html', context)

def edit_category(request, pk):
    item = Category.objects.get(pk=pk)
    if request.POST:
        form = CategoryForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('addcategory')
    else:
        form = CategoryForm(instance=item)

    return render(request, 'cart.html', {'form':form})

