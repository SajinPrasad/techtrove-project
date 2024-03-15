from django.db import models
import secrets
import string

from orders.models import Order
from user_accounts.models import Account

# Create your models here.

class Coupon(models.Model):
    code                    = models.CharField(max_length=50, unique=True)
    name                    = models.CharField(max_length=50)
    description             = models.CharField(max_length=250, null=True, blank=True)
    discount_type           = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('fixed_amount', 'Fixed Amount')))
    discount_value          = models.DecimalField(max_digits=5, decimal_places=2)
    minimum_order_value     = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active               = models.BooleanField(default=True)
    valid_from              = models.DateField(null=True, blank=True)
    valid_to                = models.DateField(null=True, blank=True)
    user                    = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, related_name='coupons')  # Optional association with a user
    applies_to_all_users    = models.BooleanField(default=False)  # Flag for common coupons
    max_usage_count         = models.PositiveIntegerField(default=1, null=True, blank=True)  # Optional maximum usage
    used_count              = models.PositiveIntegerField(default=0, null=True, blank=True)

    @staticmethod
    def generate_coupon_code(length=8):
        characters = string.ascii_uppercase + string.digits

        while True:
            coupon_code = ''.join(secrets.choice(characters) for _ in range(length))
            if not Coupon.objects.filter(code=coupon_code).exists():
                break 

        return coupon_code
    
    def used_count_for_user(self, user):
        return Order.objects.filter(user=user, coupon_code=self.code).count()

    def __str__(self):
        return f"{self.code} - {self.name}"
