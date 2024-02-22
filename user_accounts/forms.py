from django.core.validators import RegexValidator
from django import forms
from .models import Accounts

def validate_numeric(value):
    if not value.isdigit():
        raise forms.ValidationError('Phone number should only contain numeric digits.')

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Enter Password'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder' : 'Confirm Password'
    }))

    phone_number = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{10,14}$',
                message='Enter a valid phone number.',
                code='invalid_phone_number'
            ),
            validate_numeric,
        ]
    )

    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        phone_number = cleaned_data.get('phone_number')

        if password != confirm_password:
            raise forms.ValidationError('Passwords does not match!')
        
        if phone_number:
        # Check if phone_number is not None before checking its length
            if not phone_number.isdigit():
                raise forms.ValidationError('Phone number should only contain digits.')

            if len(phone_number) < 10:
                raise forms.ValidationError('Phone number should contain at least 10 digits.')

        return cleaned_data