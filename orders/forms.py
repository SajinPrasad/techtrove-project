from django import forms
from .models import Order, Payment
from userprofile.models import Address

class OrderForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['address'].queryset = Address.objects.filter(user=user)

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'order_note']

    address = forms.ModelChoiceField(
        queryset=Address.objects.all(),  # Assuming Address is the related model
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # If the address is not required
    )

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

        widgets = {'status': forms.Select(choices=Order.STATUS)}

    def __init__(self, *args, **kwargs):
        super(OrderStatusForm, self).__init__(*args, **kwargs)
        self.fields['status'].label = 'Order Status'

class PaymentStatusForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['status']
        
        widgets = {'status': forms.Select(choices=Payment.STATUS)}
        
    def __init__(self, *args, **kwargs):
        super(PaymentStatusForm, self).__init__(*args, **kwargs)
        self.fields['status'].label = 'Payment Status'
