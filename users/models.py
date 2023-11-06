from django.db import models
from django.contrib.auth.models import AbstractUser,  PermissionsMixin

# Create your models here.

class User(AbstractUser,  PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    reset_otp = models.IntegerField(max_length=255, null=True, blank=True)
    otp_request_time = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
