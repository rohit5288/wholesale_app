FROM python:3.8.5

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

RUN apt-get install -y default-mysql-client

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

# Use the shell script as the CMD
CMD ["/start.sh"]
