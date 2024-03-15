from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import models

from coupons.models import Coupon
from user_accounts.models import Account
from orders.models import Order

@receiver(post_save, sender=Account)
def create_first_time_coupon(sender, instance, created, **kwargs):
    if created:
        # Create a 'First Time' coupon for the new user
        Coupon.objects.create(
            code            = Coupon.generate_coupon_code(),
            name            = 'First Time',
            description     = "Enjoy your first purchase with a 100 rupees discount! (Only applicable for orders more than 200)",
            discount_type   = 'fixed_amount',
            discount_value  = 100,
            minimum_order_value = 200,
            is_active       = True,
            valid_from      = timezone.now(),
            valid_to        = timezone.now() + timezone.timedelta(days=365),
            user            = instance,
            applies_to_all_users = False,
            max_usage_count = 1,
        )

@receiver(post_save, sender=Order)
def generate_coupon_on_order_completion(sender, instance, **kwargs):
    # Check if the order is delivered
    if instance.status == 'Delivered':
        # Calculate the total ordered amount for the user
        total_ordered_amount = Order.objects.filter(user=instance.user, status='Delivered').aggregate(models.Sum('order_total'))['order_total__sum']

        # Check if the total ordered amount is Rs 100,000 or more
        if total_ordered_amount >= 100000:
            # Generate a coupon for the user
            Coupon.objects.create(
                code                = Coupon.generate_coupon_code(),
                name                = 'One Lakh Reward Coupon',
                description         = "Congratulations! You've reached Rs 100,000 in total ordered amount. So enjoy next order with a 100 rupees coupon. (Only applicable for orders worth RS 1000)",
                discount_type       = 'fixed_amount',
                discount_value      = 100,
                applies_to_all_users = False,
                user                = instance.user,
                is_active           = True,
                valid_from          = timezone.now(),
                valid_to            = timezone.now() + timezone.timedelta(days=365),
                max_usage_count     = 1,
            )
