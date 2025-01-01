from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import *
from django.contrib.sites.models import Site
import environ
from django.contrib.auth.hashers import make_password
from accounts.utils import *
from project.settings import *

env = environ.Env()
environ.Env.read_env()


# Function to create migrations folder with __init__.py file
class Command(BaseCommand):
    help =  """
            Create Default Super Admin
            """
    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True,role_id=ADMIN).first():
            self.stdout.write(self.style.ERROR('Admin already exists!'))
        else:
            User.objects.create(
                username="admin",
                full_name="Admin",
                email=env('DEFAULT_USERNAME'),
                password=make_password(env('DEFAULT_PASSWORD')),
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Admin created successfully!'))


        
