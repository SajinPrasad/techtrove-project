from django.db import models
from products.models import Product
from user_accounts.models import Account
from django.core.validators import MinValueValidator

# Create your models here.

class Cart(models.Model):
    cart_id         = models.CharField(max_length=100, blank=True)
    user            = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    date_added      = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart            = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity        = models.IntegerField(validators=[MinValueValidator(1)])
    is_active       = models.BooleanField(default=True)

    def __str__(self):
        return self.product

