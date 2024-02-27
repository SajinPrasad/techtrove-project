from django import forms
from django.contrib.auth.forms import UserCreationForm
from user_accounts.models import Account
from .models import UserProfile, Address
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birthdate', 'profile_pic']

class AccountForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'username']

class CombinedForm(forms.ModelForm):
    # Fields from UserProfile model
    birthdate = forms.DateField()
    profile_pic = forms.ImageField()

    # Fields from Account model
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField()
    username = forms.CharField()

    class Meta:
        model = Account  
        fields = '__all__'

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street_address', 'city', 'state', 'country', 'zip_code', 'is_primary']

