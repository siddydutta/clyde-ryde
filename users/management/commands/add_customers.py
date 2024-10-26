from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


CUSTOMERS = [
    {'username': 'john_doe', 'email': 'john_doe@clyderyde.com', 'type': 'customer'},
    {'username': 'jane_smith', 'email': 'jane_smith@clyderyde.com', 'type': 'customer'},
    {
        'username': 'michael_brown',
        'email': 'michael_brown@clyderyde.com',
        'type': 'customer',
    },
    {
        'username': 'emily_jones',
        'email': 'emily_jones@clyderyde.com',
        'type': 'customer',
    },
    {
        'username': 'william_johnson',
        'email': 'william_johnson@clyderyde.com',
        'type': 'customer',
    },
]


class Command(BaseCommand):
    help = 'Create random customers in the database'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        count = 0
        for customer_data in CUSTOMERS:
            user, created = User.objects.get_or_create(
                username=customer_data['username'],
                email=customer_data['email'],
                type=customer_data['type'],
            )
            if created:
                user.set_password('password')
                user.save()
                count += 1

        if count == 0:
            self.stdout.write(self.style.WARNING('[ADD CUSTOMERS] Skipped.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'[ADD CUSTOMERS] Successfully added {count} customers.'
                )
            )
