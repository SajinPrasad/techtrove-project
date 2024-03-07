from django.db import models
from user_accounts.models import Account
from userprofile.models import Address
from products.models import Product

# Create your models here.

class Payment(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
        ('Processing', 'Processing'),
        ('Cancelled', 'Cancelled'),
    )
    
    user            = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id      = models.AutoField(primary_key=True)
    payment_method  = models.CharField(max_length=100)
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    status          = models.CharField(max_length=15, choices=STATUS, default='Pending')
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.payment_id

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    )

    order_id        = models.AutoField(primary_key=True)
    user            = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment         = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number    = models.CharField(max_length=25)  
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    phone           = models.CharField(max_length=15)
    email           = models.EmailField()
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    address         = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    order_total     = models.DecimalField(max_digits=12, decimal_places=2)
    tax             = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee    = models.DecimalField(max_digits=5, decimal_places=2)
    status          = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered      = models.BooleanField(default=False)  
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    order_note      = models.CharField(max_length = 150, null=True, blank=True)  

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    

    
class OrderProduct(models.Model):
    order           = models.ForeignKey(Order, on_delete=models.CASCADE)
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)  
    quantity        = models.PositiveIntegerField()
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
