from django.core.management.base import BaseCommand
from core.models import Vehicle, VehicleType, Location
import random

random.seed(42)


VEHICLE_TYPES = [
    {
        'model': 'Electric Bicycle',
        'brand': 'CyclePro',
        'description': 'A bicycle with pedal assist, ideal for fitness and eco-friendly commuting.',
        'rate': 5.00,
        'image': 'vehicle_types/bike.webp',
    },
    {
        'model': 'Electric Scooter',
        'brand': 'ScootX',
        'description': 'A lightweight and foldable electric scooter suitable for city commuting.',
        'rate': 7.50,
        'image': 'vehicle_types/scooter.webp',
    },
    {
        'model': 'Electric Bike',
        'brand': 'EcoRide',
        'description': 'An electric bike with no pedal assist, perfect for longer trips and eco-friendly travel.',
        'rate': 9.00,
        'image': 'vehicle_types/electric bike.webp',
    },
]


class Command(BaseCommand):
    help = 'Add sample vehicles to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            default=10,
            help='Number of vehicles to create (default: 10)',
        )

    def handle(self, *args, **options):
        vehicle_type_ids = []
        count = 0
        for vt in VEHICLE_TYPES:
            vehicle_type, created = VehicleType.objects.get_or_create(**vt)
            if created:
                count += 1
            vehicle_type_ids.append(vehicle_type.id)
        location_ids = list(Location.objects.all().values_list('id', flat=True))
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'[ADD VEHICLES] Successfully added {count} vehicle types.'
                )
            )

        count = 0
        for _ in range(options['number']):
            vehicle, created = Vehicle.objects.get_or_create(
                **{
                    'code': str(random.randint(100000, 999999)),
                    'type_id': random.choice(vehicle_type_ids),
                    'location_id': random.choice(location_ids),
                }
            )
            if created:
                count += 1

        if count == 0:
            self.stdout.write(self.style.WARNING('[ADD VEHICLES] Skipped.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'[ADD VEHICLES] Successfully added {count} vehicles.'
                )
            )
