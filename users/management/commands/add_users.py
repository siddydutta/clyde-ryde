from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


CUSTOMERS = [
    {
        'username': 'admin',
        'email': 'admin@clyryde.com',
        'is_superuser': True,
        'is_staff': True,
    },
    {'username': 'john', 'email': 'john_doe@clyderyde.com', 'type': 'customer'},
    {'username': 'jane', 'email': 'jane_smith@clyderyde.com', 'type': 'customer'},
    {
        'username': 'emily',
        'email': 'emily_jones@clyderyde.com',
        'type': 'customer',
    },
    {
        'username': 'michael',
        'email': 'michael_brown@clyderyde.com',
        'type': 'operator',
    },
    {
        'username': 'william',
        'email': 'william_johnson@clyderyde.com',
        'type': 'manager',
    },
]


class Command(BaseCommand):
    help = 'Create random customers in the database'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        count = 0
        for customer_data in CUSTOMERS:
            user, created = User.objects.get_or_create(**customer_data)
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
