from django.contrib import admin
from core.models import Location, VehicleType, Vehicle


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'post_code',
        'address',
    )
    search_fields = (
        'name__istartswith',
        'post_code__startswith',
    )


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = (
        'model',
        'brand',
        'rate',
    )
    list_filter = ('brand',)
    search_fields = ('model__istartswith',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'status',
        'type',
        'location',
        'battery_level',
    )
    readonly_fields = ('code',)
    list_filter = (
        'status',
        'type',
        'location',
    )
    search_fields = ('code__startswith',)
