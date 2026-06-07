from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True)

    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
