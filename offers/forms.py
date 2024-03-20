from django import forms
from .models import Offer, ProductOffer, CategoryOffer
from product_category.models import Category
from products.models import Product


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = '__all__'
    
        widgets = {
            'valid_from': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (Valid From)', 'class': 'form-control'}
            ),
            'valid_to': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (Valid To)', 'class': 'form-control'}
            )
        }

    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ProductOfferForm(OfferForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all())

    class Meta(OfferForm.Meta):
        model = ProductOffer

class CategoryOfferForm(OfferForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta(OfferForm.Meta):
        model = CategoryOffer


