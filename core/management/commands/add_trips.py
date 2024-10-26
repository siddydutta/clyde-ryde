from random import choice, randint
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand

from core.models import Location, Trip, Vehicle
from customers.models import Payment


class Command(BaseCommand):
    help = 'Add random trips to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start_date',
            type=lambda d: date.fromisoformat(d),
            default=timezone.now().date() - timedelta(weeks=1),
            help='Start date for the trips (default: 1 week ago, format: YYYY-MM-DD)',
        )
        parser.add_argument(
            '--end_date',
            type=lambda d: date.fromisoformat(d),
            default=timezone.now().date(),
            help='End date for the trips (default: today, format: YYYY-MM-DD)',
        )
        parser.add_argument(
            '--number',
            type=int,
            default=10,
            help='Number of trips to create (default: 10)',
        )
        parser.add_argument(
            '--min_trip_duration',
            type=int,
            default=5,
            help='Minimum duration of a trip in minutes (default: 5)',
        )
        parser.add_argument(
            '--max_trip_duration',
            type=int,
            default=360,
            help='Maximum duration of a trip in minutes (default: 360)',
        )

    def handle(self, *args, **options):
        start_date = options['start_date']
        end_date = options['end_date']
        n_trips = options['number']

        existing_count = Trip.objects.filter(
            start_time__date__range=[start_date, end_date]
        ).count()
        if existing_count >= n_trips:
            self.stdout.write(self.style.WARNING('[ADD TRIPS] Skipped.'))
            return
        n_trips -= existing_count

        n_days = (end_date - start_date).days
        User = get_user_model()
        customers = list(User.objects.filter(type=User.Type.CUSTOMER))
        locations = list(Location.objects.all())
        vehicles = list(Vehicle.objects.all())
        count = 0
        for _ in range(n_trips):
            start_location = choice(locations)
            end_location = choice(locations)
            while start_location == end_location:
                end_location = choice(locations)
            trip_date = start_date + timedelta(days=randint(0, n_days))
            start_time = timezone.make_aware(
                timezone.datetime(
                    trip_date.year,
                    trip_date.month,
                    trip_date.day,
                    hour=randint(0, 23),
                    minute=randint(0, 59),
                )
            )
            duration = timedelta(
                minutes=randint(
                    options['min_trip_duration'], options['max_trip_duration']
                )
            )
            end_time = start_time + duration
            trip = Trip.objects.create(
                user=choice(customers),
                vehicle=choice(vehicles),
                start_time=start_time,
                end_time=end_time,
                start_location=start_location,
                end_location=end_location,
                status=Trip.Status.COMPLETED,
            )
            trip_cost = trip.compute_cost()
            Payment.objects.create(
                trip=trip,
                amount=trip_cost,
                status=Payment.Status.COMPLETED,
                paid_at=end_time,
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'[ADD TRIPS] Added {n_trips} trip(s).'))
