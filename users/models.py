from django.db import models
from django.contrib.auth.models import AbstractUser,  PermissionsMixin
from django.utils import timezone

# Create your models here.
def upload_to(instance, filename):
    return 'images/profile/{filename}'.format(filename=filename)


class User(AbstractUser,  PermissionsMixin):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to=upload_to, null=True, blank=True)
    avatar_url = models.CharField(max_length=255, null=True, blank=True)
    username = None
    reset_otp = models.IntegerField(null=True, blank=True)
    email_otp = models.IntegerField(null=True, blank=True)
    is_verified = models.BooleanField(default=False, blank=True)
    email_otp_request_time = models.DateTimeField(null=True, blank=True)
    otp_request_time = models.DateTimeField(null=True, blank=True)
    subscription_date = models.DateTimeField(null=True, blank=True)
    subscription_due_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    subscription_status = models.CharField(max_length=255, null=True, blank=True)
    expired = models.BooleanField(default=True, blank=True)
    used_free_trial = models.BooleanField(default=False, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
