from django.db import models
from user_accounts.models import Account

from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Address(models.Model):
    user            = models.ForeignKey(Account, on_delete=models.CASCADE)
    street_address  = models.CharField(max_length=200)
    city            = models.CharField(max_length=50)
    country         = models.CharField(max_length=50)
    state           = models.CharField(max_length=50)
    zip_code        = models.CharField(max_length=10)
    is_primary      = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Ensure only one primary address per user
        if self.is_primary:
            Address.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state}, {self.zip_code}"


class UserProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(blank=True, upload_to='profilepicture/')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, null=True, blank=True)

    def __str__(self):
        return self.name
    
