from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Create default users: customer, operator, manager and superuser.'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        users = [
            {
                'username': 'admin',
                'email': 'admin@clyryde.com',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'username': 'customer',
                'email': 'customer@clyderyde.com',
                'type': User.Type.CUSTOMER,
            },
            {
                'username': 'operator',
                'email': 'operator@clyryde.com',
                'type': User.Type.OPERATOR,
            },
            {
                'username': 'manager',
                'email': 'manager@clyryde.com',
                'type': User.Type.MANAGER,
            },
        ]

        for user_data in users:
            if User.objects.filter(username=user_data['username']).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"User '{user_data['username']}' already exists."
                    )
                )
                continue

            user = User.objects.create(**user_data)
            user.set_password('password')
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"User '{user_data['username']}' created successfully."
                )
            )
