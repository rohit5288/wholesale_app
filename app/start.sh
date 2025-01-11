#!/bin/bash

# until [ "`docker inspect -f {{.State.Running}} mysql-django-1`"=="true" ]; do
#     sleep 0.1;
# done;

until [ "`docker inspect -f {{.State.Health.Status}} mysql-django-1`"=="healthy" ]; do
    sleep 0.1;
done;

# until /usr/bin/docker inspect -f {{.State.Running}} local_mysql ==true $ do sleep 0.1; done; 

echo "MySQL is up - running migrations..."
python3 ./app/manage.py makemigrations
python3 ./app/manage.py migrate

echo "Adding cron jobs..."
python3 ./app/manage.py crontab add

echo "Starting cron service..."
service cron start

echo "Starting Django development server..."
python3 ./app/manage.py runserver 0.0.0.0:8000
