from django import db
from django.core.management.base import BaseCommand

from silicon.user.models import CustomUser


class Command(BaseCommand):
    help = "Create superusers users"
    superusers = [
        {
            "username": "admin",
            "email": "admin.dev@vidyamitra.ai",
            "password": "admin",
            "first_name": "VM",
            "last_name": "Admin",
        },
    ]

    def handle(self, *args, **kwargs):
        for super_user in self.superusers:
            print(super_user)
            try:
                user = CustomUser.objects.create_superuser(**super_user)
            except db.IntegrityError as e:
                print("superuser already exists.")
