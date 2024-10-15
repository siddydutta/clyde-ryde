from django.core.management.base import BaseCommand
from core.models import VehicleType


class Command(BaseCommand):
    help = 'Add sample vehicle types to the database'

    def handle(self, *args, **kwargs):
        vehicle_types = [
            {
                'model': 'E-Scooter',
                'brand': 'ScootX',
                'description': 'A lightweight and foldable electric scooter suitable for city commuting.',
                'rate': 7.50,
            },
            {
                'model': 'E-Bike',
                'brand': 'EcoRide',
                'description': 'An electric bike with pedal-assist, perfect for longer trips and eco-friendly travel.',
                'rate': 9.00,
            },
        ]

        for vehicle_data in vehicle_types:
            VehicleType.objects.create(**vehicle_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully added {vehicle_data["model"]}')
            )
