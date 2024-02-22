from django import forms
from . models import Products, Images
from multiupload.fields import MultiFileField

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['product_name', 'slug', 'description', 'price', 'stock', 'category', 'is_available',]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    # def clean_images(self):
    #     images = self.cleaned_data.get('images')

    #     if not image:
    #         raise forms.ValidationError("No images provided.")

    #     for image in images:
    #         if not image.content_type.startswith('image'):
    #             raise forms.ValidationError("Invalid file type. Please upload an image.")

    #         max_size = 5 * 1024 * 1024
    #         if image.size > max_size:
    #             raise forms.ValidationError("File size exceeds the maximum limit (5 MB).")

    #     return images
            
class ImageForm(forms.ModelForm):
    image = MultiFileField(
        min_num=1,
        max_num=5,
        max_file_size=1024*1024*5,  # 5 MB
        allow_empty_file=False,
        label='Image',
    )

    class Meta:
        model = Images
        fields = ['image']

