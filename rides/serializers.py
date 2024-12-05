from rest_framework import serializers
from .models import *

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        
        return user


class RideSerializer(serializers.ModelSerializer):
    rider = CustomUserSerializer(read_only=True)
    driver = CustomUserSerializer(read_only=True)

    class Meta:
        model = Ride
        fields = '__all__'


