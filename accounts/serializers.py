from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer

from .models import CustomerProfile


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'phone', 'first_name', 'last_name']


class UserSerializer(DjoserUserSerializer):
    class Meta(DjoserUserSerializer.Meta):
        fields = ['id', 'username', 'phone', 'first_name', 'last_name']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'city', 'address']
