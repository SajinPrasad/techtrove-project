from django.db import models
from user_accounts.models import Account
from userprofile.models import Address
from products.models import Product

from django.core.validators import MinValueValidator

from django.core.validators import MinValueValidator

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
    transaction_id  = models.CharField(max_length=255, unique=True, null=True, blank=True)
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
    order_total     = models.DecimalField(max_digits=16, decimal_places=2)
    tax             = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee    = models.DecimalField(max_digits=5, decimal_places=2)
    coupon_applied  = models.CharField(max_length=50, null=True, blank=True)
    coupon_discount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    coupon_code     = models.CharField(max_length=50, null=True, blank=True)
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
    product_image   = models.ImageField(upload_to='photos/order_products', blank=True, null=True)
    product_name    = models.CharField(max_length=150,null=True, blank=True)
    price           = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    description     = models.TextField(max_length=700, blank=True, null=True)
    category        = models.CharField(max_length=150, blank=True, null=True)
    quantity        = models.PositiveIntegerField()
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    offer_title     = models.CharField(max_length=100, null=True, blank=True)
    offer_discount_type   = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('fixed_amount', 'Fixed Amount')), null=True, blank=True)
    offer_discount_value  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class Wallet(models.Model):
    user            = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance         = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Transaction(models.Model):
    wallet          = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    order           = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    created_at      = models.DateTimeField(auto_now_add=True)
    description     = models.TextField(max_length = 200, null=True, blank=True)    
