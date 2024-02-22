from django.shortcuts import render, redirect
from .forms import ProductForm, ImageForm
from .models import Images
from django.contrib import messages

# Create your views here.

def add_product(request):
    imgform = None
    if request.POST:
        form = ProductForm(request.POST)
        images = request.FILES.getlist('image')
        if form.is_valid():
            f = form.save(commit=False)
            form.save()
            form = ProductForm()
            for i in images:
                Images.objects.create(product=f, image=i)
            messages.success(request, 'Added new prodect')
            return redirect('addproduct')
    else:
        form = ProductForm()
        imgform = ImageForm()
    context = {'form':form, 'imgform':imgform}
    return render(request, 'add_product.html', context)
