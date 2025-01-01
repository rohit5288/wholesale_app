from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import *
from django.contrib.sites.models import Site
import environ
from django.contrib.auth.hashers import make_password
from accounts.utils import *

env = environ.Env()
environ.Env.read_env()

class Command(BaseCommand):
    help = "Adding default values to Database by Admin"
    def handle(self, *args, **options):
        fees,created=AdminServiceFees.objects.get_or_create(service_fees=DEFAULT_SERVICE_FEES)
        if created:
            self.stdout.write(self.style.SUCCESS('Service Fees Added Successfully!'))