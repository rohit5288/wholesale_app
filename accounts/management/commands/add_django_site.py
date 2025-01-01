from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import *
from django.contrib.sites.models import Site
import environ
from django.contrib.auth.hashers import make_password

env = environ.Env()
environ.Env.read_env()


class Command(BaseCommand):
    help = "Adding default values to Database by Admin"
    def handle(self, *args, **options):
        try:        
            user=User.objects.get(is_superuser=True, role_id=ADMIN)
        except:
            self.stdout.write(self.style.NOTICE("Admin rights, Create Admin First"))
            return None
        try:
            site = Site.objects.get(pk=settings.SITE_ID)
        except:
            site = Site.objects.create(pk=settings.SITE_ID)
        site.domain = env('SITE_DOMAIN')
        site.name = env('SITE_DOMAIN')
        site.save()
        self.stdout.write(self.style.SUCCESS('Site Domain Updated Successfully!'))
