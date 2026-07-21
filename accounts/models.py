from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib import admin

    
class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
