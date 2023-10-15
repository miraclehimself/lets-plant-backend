from rest_framework import serializers
from .models import processPlant

class processPlantSerilizer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source = 'user.id')
    plant_image = serializers.ImageField(required=True)
    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)

    class Meta:
        model = processPlant
        fields = '__all__'
        read_only_fields = ('id', 'user_id')
        required_fields = ('user_id', 'plant_image', 'longitude', 'latitude')
        
        