from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import *
from django.contrib.sites.models import Site
import environ
from django.contrib.auth.hashers import make_password
from accounts.utils import *
from subscriptions.models import *

env = environ.Env()
environ.Env.read_env()

class Command(BaseCommand):
    help = "Adding default values to Database by Admin"
    def handle(self, *args, **options):
        for data in DefaultSubscriptions(): 
            if not SubscriptionPlans.objects.filter(title=data['title'],validity=data['validity']).exists():
                SubscriptionPlans.objects.create(
                    title = data['title'] if data['title'] else "",
                    features = data['description'] if data['description'] else "",
                    price = data['price'] if data['price'] else "",
                    validity = data['validity'] if data['validity'] else "",
                )      
        self.stdout.write(self.style.SUCCESS('Subscriptions Plans Added Successfully!'))

        for data in DefaultBoosterPlans(): 
            if not EventBoosterPlans.objects.filter(title=data['title'],days=data['days']).exists():
                EventBoosterPlans.objects.create(
                    title = data['title'] if data['title'] else "",
                    features = data['description'] if data['description'] else "",
                    price = data['price'] if data['price'] else "",
                    days = data['days'] if data['days'] else "",
                )      
        self.stdout.write(self.style.SUCCESS('Booster Plans Added Successfully!'))

        fees,created=AdminServiceFees.objects.get_or_create(service_fees=DEFAULT_SERVICE_FEES)
        if created:
            self.stdout.write(self.style.SUCCESS('Service Fees Added Successfully!'))