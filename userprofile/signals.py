from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from userprofile.models import UserProfile, Address

@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=get_user_model())
# def create_user_address(sender, instance, created, **kwargs):
#     if created:
#         Address.objects.create(user=instance, is_primary=True, street_address='', city='', country='', state='', zip_code='')

# @receiver(post_save, sender=get_user_model())
# def save_user_address(sender, instance, **kwargs):
#     instance.address.save()