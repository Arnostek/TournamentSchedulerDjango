FROM python:3-stretch

RUN apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y \
      build-essential python-dev; \
    pip install django numpy pandas

ENTRYPOINT python /srv/django/manage.py runserver 0.0.0.0:8844
