from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import *
from django.contrib.sites.models import Site
import environ
from accounts.utils import *
from accounts.models import *
import stripe

env = environ.Env()
environ.Env.read_env()

stripe.api_key=GetStripeKey()
class Command(BaseCommand):
    help = "Adding Buyer Id's For user"
    def handle(self, *args, **options):
        running = True
        users=User.objects.all().exclude(role_id=ADMIN)
        if not users:
            running=False
            self.stdout.write(self.style.ERROR('There is no user registered with Base.'))
        for user in users:
            if not user.customer_id:
                try:
                    stripe_customer = stripe.Buyer.create(
                            description = "Base User - %s " % user.email,
                            email = user.email,
                            name = user.email,
                        )
                    user.customer_id = stripe_customer.id
                    user.save()
                    running=True
                except Exception as e:
                    self.stdout.write(self.style.ERROR('Something went wrong! due to following ERROR.'))
                    self.stdout.write(self.style.HTTP_NOT_FOUND(e))
                    running=False
                    break
            else:
                pass
        if running:
            self.stdout.write(self.style.SUCCESS('Users registered successfully with stripe!'))
