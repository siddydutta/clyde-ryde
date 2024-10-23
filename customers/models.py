from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from core.models import Trip, Location, Vehicle
import random

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='wallet'
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.balance}'

    def debit(self, amount: Decimal) -> bool:
        if amount > self.balance:
            return False
        self.balance -= amount
        self.save(update_fields=['balance'])
        return True


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = ('pending', _('Pending'))
        COMPLETED = ('completed', _('Completed'))

    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    paid_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.trip} - {self.amount}'

    def complete_payment(self):
        self.status = Payment.Status.COMPLETED
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at'])



class Report(models.Model):
    class Status(models.TextChoices):
        BROKE = ('broke', _('Broke'))
        GOOD = ('good', _('Good'))

    report_id = models.CharField(max_length=6, unique=True, primary_key=True)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.GOOD
    )
    vehicle_code = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='broke_vehicle'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name='broke_vehicles_location'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    description = models.TextField()

    def save(self, *args, **kwargs):
        if not self.report_id:
            self.report_id = self.__generate_unique_id()
        super().save(*args, **kwargs)

    def __generate_unique_id(self):
        while True:
            report_id = str(random.randint(100000, 999999))
            if not Report.objects.filter(report_id=report_id).exists():
                return report_id
