from django import forms
from . models import Product, Image
from multiupload.fields import MultiFileField

# Product form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'slug', 'description', 'price', 'stock', 'category', 'is_available',]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        # self.fields['description'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 4})

# Image form
class ImageForm(forms.ModelForm):
    image = MultiFileField(
        min_num=1,
        max_num=5,
        max_file_size=1024*1024*5,  # 5 MB
        label='Image',
    )

    class Meta:
        model = Image
        fields = ['image']

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

