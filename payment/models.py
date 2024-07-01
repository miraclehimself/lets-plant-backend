from django.db import models
from users.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_requests")
    amount = models.CharField(max_length=255, null=True,blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    identity = models.CharField(max_length=255,blank=True, null=True)
    successful = models.BooleanField(null=True, default=False)
    meta_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gocardless_customer_id = models.CharField(max_length=255, blank=True, null=True)
    mandate_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.user.username
    
class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subscription_type} for {self.customer.user.username}"