from django.db import models
from django.contrib.auth.models import AbstractUser
import random

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('rider', 'Rider'),
        ('driver', 'Driver'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='rider')
    ride_code = models.CharField(max_length=4, unique=True, blank=True, null=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.ride_code:
            self.ride_code = self.generate_unique_ride_code()
        super().save(*args, **kwargs)

    def generate_unique_ride_code(self):
        while True:
            code = str(random.randint(1000, 9999))
            if not CustomUser.objects.filter(ride_code=code).exists():
                return code


class Ride(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), 
        ('ACCEPTED', 'Accepted'),
        ('STARTED', 'Started'),  
        ('COMPLETED', 'Completed'),  
        ('CANCELLED', 'Cancelled'),
    ]

    rider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rides_as_rider')
    driver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='rides_as_driver')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride {self.id} - {self.status}"



