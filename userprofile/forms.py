from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_accounts.models import Account
from .models import UserProfile, Address
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django.forms import ClearableFileInput

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birthdate', 'gender', 'profile_pic']

        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control'}),
            'profile_pic': ClearableFileInput(attrs={'class': 'form-control'}),
        }

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'username']

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        # Exclude password fields
        self.fields.pop('password', None)

# class CombinedForm(forms.ModelForm):
#     # Fields from UserProfile model
#     birthdate = forms.DateField()
#     profile_pic = forms.ImageField()

#     # Fields from Account model
#     first_name = forms.CharField()
#     last_name = forms.CharField()
#     email = forms.EmailField()
#     phone_number = forms.CharField()
#     username = forms.CharField()

#     class Meta:
#         model = Account  
#         fields = '__all__'

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line','street_name', 'city', 'state', 'country', 'zip_code', 'is_primary']

