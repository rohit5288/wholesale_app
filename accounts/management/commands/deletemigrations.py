from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import *
from django.contrib.sites.models import Site
import environ
from django.contrib.auth.hashers import make_password
from accounts.utils import *
from subscriptions.models import *
from django.db.migrations.recorder import MigrationRecorder
from project.settings import *

env = environ.Env()
environ.Env.read_env()


# Function to create migrations folder with __init__.py file
class Command(BaseCommand):
    help =  """
            1.Delete migrations for each apps.
            2.Create migratons folder with init file in all apps that do not already have.
            """
    def create_migrations_folder(self,app_name):
        migrations_path = os.path.join(app_name, 'migrations')
        if not os.path.exists(migrations_path):
            os.makedirs(migrations_path)
            open(os.path.join(migrations_path, '__init__.py'), 'a').close()
            self.stdout.write(self.style.SUCCESS(f"Created migrations folder in {app_name.split('/')[-1]} app"))
            return True
        return False

    def handle(self, *args, **options):
        confirm = input("Do you want to delete migrations from all apps? (y/n): ").lower().strip()
        if confirm == 'y':
            try:
                os.system('find . -path "*/migrations/[0-9][0-9][0-9][0-9]_*.py" -not -name "__init__.py" -delete')
                os.system('find . -path "*/migrations/*.pyc" -delete')
            except Exception as e:
                self.stdout.write(self.style.ERROR('Something went wrong! due to following ERROR.'))
                self.stdout.write(self.style.HTTP_NOT_FOUND(e))
            # confirm=input("Do you want to clear database? (y/n):")
            # if confirm == 'y':
            #     try:
            #         MigrationRecorder.Migration.objects.all().delete()
            #     except Exception as e:
            #         self.stdout.write(self.style.ERROR('Something went wrong! due to following ERROR.'))
            #         self.stdout.write(self.style.HTTP_NOT_FOUND(e))
            # self.stdout.write(self.style.SUCCESS('Migrations deleted Successfully!'))

        confirm = input("Do you want to add a migrations folder to each app that doesn't already have one?? (y/n): ").lower().strip()
        if confirm == 'y':
            try:
                # Directory where your Django project is located
                project_directory = os.getcwd()
                # List all directories (apps) in the project directory
                apps = [name for name in os.listdir(project_directory) if os.path.isdir(os.path.join(project_directory, name))]
                # Exclude specific directories
                exclude_dirs = ['media', 'static', 'project','templates','env','screenshot']
                included_dirs = INSTALLED_APPS[15:]
                # Loop through each app directory and create migrations folder if it doesn't exist
                is_created=[]
                for app in apps:
                    if app in included_dirs:
                        is_created.append(self.create_migrations_folder(os.path.join(project_directory,app)))
                if True in is_created:
                    self.stdout.write(self.style.SUCCESS('Migrations folder created successfully!'))
                else:
                    self.stdout.write(self.style.ERROR('Migrations folder already exist in all apps!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR('Something went wrong! due to following ERROR.'))
                self.stdout.write(self.style.HTTP_NOT_FOUND(e))

        
