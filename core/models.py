import random

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class VehicleType(models.Model):
    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    description = models.TextField()
    rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text=_('Hourly rental rate')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model


class Vehicle(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = ('available', _('Available'))
        IN_USE = ('in_use', _('In use'))

    code = models.CharField(max_length=6, unique=True, primary_key=True)
    status = models.CharField(max_length=10, choices=Status.choices)
    type = models.ForeignKey(
        VehicleType, on_delete=models.CASCADE, related_name='vehicles'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name='vehicles'
    )
    battery_level = models.IntegerField(
        default=100, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        while True:
            code = str(random.randint(100000, 999999))
            if not Vehicle.objects.filter(code=code).exists():
                return code
