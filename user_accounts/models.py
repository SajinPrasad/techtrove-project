from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission
import uuid

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

class Accounts(AbstractUser):
    objects = MyAccountManager()

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    otp = models.IntegerField(null=True, blank=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    groups = models.ManyToManyField(Group, related_name='user_accounts_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_accounts_permissions')

    def __str__(self):
        return self.email

