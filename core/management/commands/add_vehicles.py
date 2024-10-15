from django.core.management.base import BaseCommand
from core.models import Vehicle, VehicleType, Location
import random


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
        vehicle_types = VehicleType.objects.all()[:2]
        locations = Location.objects.all()[:5]

        for _ in range(options['number']):
            vehicle = Vehicle.objects.create(
                **{
                    'type': random.choice(vehicle_types),
                    'location': random.choice(locations),
                }
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully added vehicle {vehicle.code} ({vehicle.type.model})'
                )
            )
