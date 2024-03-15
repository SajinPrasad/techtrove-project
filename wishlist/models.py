from django.db import models
from django.core.validators import MinValueValidator

from user_accounts.models import Account
from products.models import Product

# Create your models here.

class Wishlist(models.Model):
    user        = models.ForeignKey(Account, on_delete=models.CASCADE)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity    = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at  = models.DateTimeField(auto_now_add=True)
