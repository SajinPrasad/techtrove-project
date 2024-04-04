from django.db import models
from products.models import Product
from user_accounts.models import Account
from django.core.validators import MinValueValidator
from offers.models import ProductOffer, CategoryOffer

# Create your models here.

class Cart(models.Model):
    cart_id         = models.CharField(max_length=100, blank=True)
    user            = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    date_added      = models.DateField(auto_now_add=True)
    cart_total      = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    coupon_name     = models.CharField(max_length=50, null=True, blank=True)
    coupon_code      = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart                = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity            = models.IntegerField(validators=[MinValueValidator(1)])
    variation_category  = models.CharField(max_length=100, null=True, blank=True)
    variation_value     = models.CharField(max_length=100, null=True, blank=True)
    is_active           = models.BooleanField(default=True)
    product_offer       = models.ForeignKey(ProductOffer, on_delete=models.CASCADE, null=True, blank=True)
    category_offer      = models.ForeignKey(CategoryOffer, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.product

