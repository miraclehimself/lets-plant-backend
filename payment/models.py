from django.db import models
from users.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_requests")
    amount = models.CharField(max_length=255, null=True,blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    identity = models.FloatField(null=True)
    successful = models.BooleanField(null=True, default=False)
    meta_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)