from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source = 'user.id')
    amount = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)
    identity = serializers.CharField(required=False)
    successful = serializers.BooleanField(required=False)
    meta_data = serializers.JSONField(required=False)

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('id', 'user_id')
        # required_fields = ('user_id', 'plant_image', 'longitude', 'latitude')
    