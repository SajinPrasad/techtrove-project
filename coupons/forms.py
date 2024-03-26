from django.forms import ModelForm
from django import forms
from .models import Coupon
import secrets
import string

class CouponForm(ModelForm):
    class Meta:
        model = Coupon
        fields = ['name', 'description', 'discount_type', 'discount_value', 'minimum_order_value', 'is_active', 'valid_from', 'valid_to', 'applies_to_all_users', 'max_usage_count', ]

        widgets = {
            'valid_from': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (Valid From)', 'class': 'form-control'}
            ),
            'valid_to': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd (Valid To)', 'class': 'form-control'}
            ),
            'applies_to_all_users': forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input', 'id': "flexCheckDefault"}),
            'is_active': forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check-input',  'id': "flexCheckDefault"}),
        }

    def __init__(self, *args, **kwargs):
        super(CouponForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'applies_to_all_users' and field != 'is_active':
                self.fields[field].widget.attrs['class'] = 'form-control'

    @staticmethod
    def generate_coupon_code(length=8):
        characters = string.ascii_uppercase + string.digits

        while True:
            coupon_code = ''.join(secrets.choice(characters) for _ in range(length))
            if not Coupon.objects.filter(code=coupon_code).exists():
                break 

        return coupon_code

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Generate coupon code using the static method
        instance.code = self.generate_coupon_code()

        if commit:
            instance.save()

        return instance        
