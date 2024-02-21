from django.db import models
from users.models import User

def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)

class processPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="proccessed_plant_requests")
    name = models.CharField(max_length=255, null=True,blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    plant_image = models.ImageField(upload_to=upload_to)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    water_frequency = models.CharField(max_length=255, null=True, blank=True)
    sun_frequency = models.CharField(max_length=255, null=True, blank=True)
    soil_type = models.CharField(max_length=255, null=True, blank=True)
    symptoms = models.CharField(max_length=255, null=True, blank=True)
    recommendation = models.TextField(null=True,blank=True)
    meta_data = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)