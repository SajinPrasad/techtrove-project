from django.db import models
from product_category.models import Category
from django.core.validators import MinValueValidator

# Create your models here.

class Product(models.Model):
    product_name        = models.CharField(max_length=150, unique=True)
    slug                = models.SlugField(max_length=150, unique=True)
    description         = models.TextField(max_length=700, blank=True)
    price               = models.IntegerField(validators=[MinValueValidator(1)])
    stock               = models.IntegerField(validators=[MinValueValidator(0)])
    is_available        = models.BooleanField(default=True)
    category            = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date        = models.DateTimeField(auto_now_add=True)
    modified_date       = models.DateTimeField(auto_now=True)
    is_deleted          = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name
    
class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/products', null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
