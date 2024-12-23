import random
from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
    image = models.ImageField(upload_to='vehicle_types/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.model


class Vehicle(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = ('available', _('Available'))
        IN_USE = ('in_use', _('In use'))
        DEFECTIVE = ('defective', _('Defective'))
        DISCHARGED = ('discharged', _('Discharged'))

    code = models.CharField(max_length=6, unique=True, primary_key=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.AVAILABLE
    )
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

    def __str__(self):
        return f'{self.code} - {self.type.model}'

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.__generate_unique_code()
        if self.battery_level == 0 and self.status != Vehicle.Status.DEFECTIVE:
            self.status = Vehicle.Status.DISCHARGED
        super().save(*args, **kwargs)

    def __generate_unique_code(self):
        while True:
            code = str(random.randint(100000, 999999))
            if not Vehicle.objects.filter(code=code).exists():
                return code

    def update_battery_level(self, duration: int) -> None:
        """Update battery level based on the duration (seconds) of the trip."""
        self.battery_level -= 0.1 * duration
        self.battery_level = max(self.battery_level, 0)


class Trip(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = ('in_progress', _('In Progress'))
        COMPLETED = ('completed', _('Completed'))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='trips',
    )
    vehicle = models.ForeignKey(
        Vehicle, null=True, on_delete=models.SET_NULL, related_name='trips'
    )
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    start_location = models.ForeignKey(
        Location, null=True, on_delete=models.SET_NULL, related_name='trip_starts'
    )
    end_location = models.ForeignKey(
        Location, null=True, on_delete=models.SET_NULL, related_name='trip_ends'
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['start_time']),
        ]

    def __str__(self):
        return f'Trip #{self.pk} by {self.user} on {self.vehicle}'

    def end_trip(self, end_location: Location) -> None:
        self.end_time = timezone.now()
        self.end_location = end_location
        self.status = Trip.Status.COMPLETED
        self.vehicle.location = end_location
        if self.vehicle.status == Vehicle.Status.IN_USE:
            self.vehicle.status = Vehicle.Status.AVAILABLE
        self.vehicle.update_battery_level(self.duration)
        self.vehicle.save(update_fields=['location', 'status', 'battery_level'])
        self.save(update_fields=['end_time', 'end_location', 'status'])

    @property
    def duration(self) -> Optional[float]:
        """Calculates trip duration in seconds."""
        if not self.end_time:
            return None
        return (self.end_time - self.start_time).total_seconds()

    @property
    def formatted_duration(self) -> Optional[str]:
        duration = self.duration
        if duration is None:
            return None
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        return f'{hours}h {minutes}m {seconds}s'

    def compute_cost(self) -> Optional[Decimal]:
        if self.duration is None:
            return None
        rate = self.vehicle.type.rate
        duration_in_hours = Decimal(self.duration) / Decimal(3600)
        cost = rate * duration_in_hours
        return cost.quantize(Decimal('0.01'))  # Round to 2 decimal places
