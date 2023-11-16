from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, default='./images/profile/avatar.png')
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'avatar', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        email = serializers.CharField(required=False, allow_blank=True)
        password = serializers.CharField()
        
class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'avatar']
        name =  serializers.CharField(required=True)
        avatar = serializers.ImageField(required=False)