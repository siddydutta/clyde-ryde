from django.db.models.signals import post_save
from django.dispatch import receiver

from core.cache import cache
from core.constants import VEHICLE_TYPES_CACHE_KEY
from core.models import VehicleType


@receiver(post_save, sender=VehicleType)
def post_save_vehicle_type(sender, instance, **kwargs):
    cache.delete(VEHICLE_TYPES_CACHE_KEY)
