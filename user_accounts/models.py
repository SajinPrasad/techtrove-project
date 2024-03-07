from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission
import uuid
from django_otp.models import ThrottlingMixin
from django_otp.plugins.otp_totp.models import TOTPDevice as BaseTOTPDevice

# Create your models here.

class MyAccountManager(UserManager):
    def create_user(self, first_name, last_name, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

class Account(AbstractUser):
    objects         = MyAccountManager()

    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=100, unique=True)
    phone_number    = models.CharField(max_length=20)
    otp             = models.IntegerField(null=True, blank=True)
    uid             = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_verified     = models.BooleanField(default=False)
    is_blocked      = models.BooleanField(default=False)

    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    groups          = models.ManyToManyField(Group, related_name='user_accounts_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_accounts_permissions')

    def __str__(self):
        return self.email

   

class OTPModel(ThrottlingMixin):
    key = models.CharField(max_length=40, unique=True, editable=False)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.key}"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)


class TOTPDevice(BaseTOTPDevice):
    def generate_otp(self):
        """
        Generate a time-based one-time password (TOTP).
        """
        return self.token_generator.generate_token(self)



