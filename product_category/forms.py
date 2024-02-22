from django import forms
from .models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_images(self):
        image = self.cleaned_data.get('images')

        if not image:
            raise forms.ValidationError("No image provided.")

        if not image.content_type.startswith('image'):
            raise forms.ValidationError("Invalid file type. Please upload an image.")

        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            raise forms.ValidationError("File size exceeds the maximum limit (5 MB).")

        return image