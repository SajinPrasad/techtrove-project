from django.db import models
from django.utils import timezone
from products.models import Product
from product_category.models import Category

# Create your models here.

class Offer(models.Model):
    CHOICES = (
        ('PRODUCT', 'Product offer'),
        ('CATEGORY', 'Category offer')
    )

    title           = models.CharField(max_length=100)
    description     = models.CharField(max_length=250, blank=True)
    discount_type   = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('fixed_amount', 'Fixed Amount')))
    discount_value  = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from      = models.DateTimeField(default=timezone.now)
    valid_to        = models.DateTimeField()
    is_active       = models.BooleanField(default=True)
    offer_type      = models.CharField(max_length=15, choices=CHOICES)

    class Meta:
        abstract = True


class ProductOffer(Offer):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Product Offer"

    def apply_offer(self, cart_item):
        if cart_item.product == self.product:
            discount = 0
            if self.discount_type == 'fixed_amount':
                discounted_amount = cart_item.product_price - self.discount_value
            else:
                discount = cart_item.product_price * (self.discount_value / 100)
                discounted_amount = cart_item.product_price - discount
        else:
            discounted_amount = cart_item.product_price

        return discounted_amount
    
    def get_the_offer(self, cart_item):
        if cart_item.product == self.product:
            return self
        else:
            return None
        
    def get_the_offer_for_product(self, product):
        if product == self.product:
            return self
        else:
            return None
        
    def products_with_offer(self, product):
        if product == self.product:
            return product
        else:
            return self


class CategoryOffer(Offer):
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Category Offer"

    def apply_offer(self, cart_item):
        if cart_item.product.category == self.category:
            discount = 0
            if self.discount_type == 'fixed_amount':
                discounted_amount = cart_item.product_price - self.discount_value
            else:
                discount = cart_item.product_price * (self.discount_value / 100)
                discounted_amount = cart_item.product_price - discount
        else:
            discounted_amount = cart_item.product_price

        return discounted_amount
    
    def get_the_offer(self, cart_item):
        if cart_item.product.category == self.category:
            return self
        else:
            return None
        
    def get_the_offer_for_product(self, product):
        if product.category == self.category:
            return self
        else:
            return None
        
    def products_with_offer(self, product):
        if product.category == self.category:
            return product
        else:
            return None

        