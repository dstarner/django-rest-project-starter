import time

from django.contrib.auth import get_user_model

from ..base import AdminCommand


class Command(AdminCommand):

    EMAIL = 'superuser@localhost'
    PASSWORD = 'hunter2'

    def handle(self, *args, **options):
        self.info('Sleeping for 10 seconds to wait for migrations')
        time.sleep(10)

        User = get_user_model()

        user = None if User.objects.filter(email=self.EMAIL).exists() else User.objects.create_superuser(
            email=self.EMAIL, password=self.PASSWORD, first_name='Admin', last_name='McAdmin'
        )
        self.info(
            f'!! {self.EMAIL}:{self.PASSWORD} user already exists !!'
        ) if not user else self.success(
            f"!! {self.EMAIL} user created with password '{self.PASSWORD}' !!"
        )
