from django.core.management.base import BaseCommand
from core.models import Location


class Command(BaseCommand):
    help = 'Add sample locations to the database'

    def handle(self, *args, **kwargs):
        locations = [
            {
                'name': 'Clyde Ryde - George Square',
                'address': 'George Square, Glasgow',
                'post_code': 'G2 1DU',
                'latitude': 55.860916,
                'longitude': -4.250484,
            },
            {
                'name': 'Clyde Ryde - Glasgow Green',
                'address': 'Glasgow Green, Glasgow',
                'post_code': 'G40 1AT',
                'latitude': 55.848349,
                'longitude': -4.236811,
            },
            {
                'name': 'Clyde Ryde - Buchanan Bus Station',
                'address': 'Killermont St, Glasgow',
                'post_code': 'G2 3NW',
                'latitude': 55.864237,
                'longitude': -4.251806,
            },
            {
                'name': 'Clyde Ryde - Kelvingrove Park',
                'address': 'Kelvin Way, Glasgow',
                'post_code': 'G3 7TH',
                'latitude': 55.868845,
                'longitude': -4.283497,
            },
            {
                'name': 'Clyde Ryde - University of Glasgow',
                'address': 'University Avenue, Glasgow',
                'post_code': 'G12 8QQ',
                'latitude': 55.872120,
                'longitude': -4.288090,
            },
        ]

        for location_data in locations:
            Location.objects.create(**location_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully added {location_data["name"]}')
            )
