from django import forms
from . models import Product, Image
from multiupload.fields import MultiFileField
from product_category.models import Category
from django.forms import inlineformset_factory

# Product form
class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.exclude(is_deleted=True), required=False)
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'stock', 'category', 'is_available']

        widgets = {
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_available':
                self.fields[field].widget.attrs['class'] = 'form-control'

ImageFormSet = inlineformset_factory(Product, Image, fields=['image'], extra=1, can_delete=True)

    

        # self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 4})

# Image form
class ImageForm(forms.ModelForm):
    image = MultiFileField(
        min_num=0,
        max_num=5,
        max_file_size=1024*1024*5,  # 5 MB
        label='Image',
        required=False,  
    )

    class Meta:
        model = Image
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = False  # Ensure required=False is set here
        self.fields['image'].initial = [] 

    def clean_image(self):
        images = self.cleaned_data.get('image')

        if not images:
            raise forms.ValidationError("No images provided.")

        for image in images:
            if not image.content_type.startswith('image'):
                raise forms.ValidationError("Invalid file type. Please upload an image.")

            max_size = 5 * 1024 * 1024
            if image.size > max_size:
                raise forms.ValidationError("File size exceeds the maximum limit (5 MB).")

        return images

