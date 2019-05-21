FROM python:3-stretch

RUN apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y \
      build-essential python-dev; \
    pip install --upgrade pip; \
    pip install django numpy pandas "ipython[notebook]" django_extensions


ENTRYPOINT python /srv/django/manage.py runserver 0.0.0.0:8844
